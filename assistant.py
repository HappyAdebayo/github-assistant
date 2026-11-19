from dotenv import load_dotenv
from config import MODEL_NAME, GENERATION_CONFIG,CONTEXT_WINDOW
from google import genai
from google.genai import types
from prompt import SYSTEM_INSTRUCTION
from tools import GITHUB_TOOLS
import os
from tool_executor import execute_tool

load_dotenv()

api_key=os.getenv("GEMINI_API_KEY")

client= genai.Client(api_key=api_key)

conversation_history=[]
MAX_TOOL_ITERATIONS = 5



def trim_context():
    while True:
        token_count = client.models.count_tokens(
            model=MODEL_NAME,
            contents=conversation_history
        ).total_tokens

        if token_count <= CONTEXT_WINDOW:
            print(f"Context usage: {token_count}/{CONTEXT_WINDOW}")
            return

        user_turns = [
            index
            for index, message in enumerate(conversation_history)
            if (
                message.get("role") == "user"
                if isinstance(message, dict)
                else message.role == "user"
            )
            and any(
                part.get("text") is not None
                if isinstance(part, dict)
                else getattr(part, "text", None) is not None
                for part in (
                    message.get("parts", [])
                    if isinstance(message, dict)
                    else message.parts
                )
            )
        ]

        if len(user_turns) <= 1:
            raise ValueError(
                "Current message exceeds the configured context window."
            )

        print("Context window exceeded. Removing oldest conversation turn...")
        del conversation_history[user_turns[0]:user_turns[1]]

        
def chat_with_assistant(user_message):
    tool_iterations = 0
    conversation_history.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })
    trim_context()
    try:
        response =client.models.generate_content(
            model=MODEL_NAME,
            contents=conversation_history,
            config=types.GenerateContentConfig(
                temperature=GENERATION_CONFIG['temperature'],
                tools=GITHUB_TOOLS,
                max_output_tokens=GENERATION_CONFIG['max_output_tokens'],
                system_instruction=SYSTEM_INSTRUCTION
            )
        )

        model_content = response.candidates[0].content

        while tool_iterations < MAX_TOOL_ITERATIONS:
            function_calls =[
                part.function_call
                for part in model_content.parts
                if part.function_call
            ]

            if not function_calls:
                conversation_history.append(
                    model_content.model_dump(
                        exclude_none=True,
                    )
                )

                for part in model_content.parts:
                    if part.text:
                        print(part.text)

                break

            tool_iterations +=1

            conversation_history.append(
                model_content.model_dump(
                    exclude_none=True,
                )
            )
            
            function_response_parts=[]
            
            print(f"Function calls in this round: {len(function_calls)}")
            
            for function_call in function_calls:
                print(f"Tool: {function_call.name}")
                print(f"Arguments: {function_call.args}")
                result = execute_tool(function_call)

                function_response_parts.append(
                    types.Part.from_function_response(
                        name=function_call.name,
                        response={"result": result}
                    )
                )

            tool_response_content = types.Content(
                    role="user",
                    parts=function_response_parts
                )

            conversation_history.append(tool_response_content)


            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=conversation_history,
                config=types.GenerateContentConfig(
                    temperature=GENERATION_CONFIG["temperature"],
                    tools=GITHUB_TOOLS,
                    max_output_tokens=GENERATION_CONFIG["max_output_tokens"],
                    system_instruction=SYSTEM_INSTRUCTION
                )
            )
  
            model_content = response.candidates[0].content

        else:
             print("Maximum tool-call iterations reached.")
        
    except Exception as e:
        print(f"An error occured while communicating with gemini {e}")
