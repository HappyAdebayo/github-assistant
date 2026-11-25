from dotenv import load_dotenv
from config import MODEL_NAME, GENERATION_CONFIG,CONTEXT_WINDOW
from google import genai
from google.genai import types
from prompt import SYSTEM_INSTRUCTION
from tools import GITHUB_TOOLS
import os
from tool_executor import execute_tool
import json
from conversation_manager import ConversationManager
from context_manager import ContextManager

load_dotenv()

api_key=os.getenv("GEMINI_API_KEY")

client= genai.Client(api_key=api_key)

conversation_manager = ConversationManager()
context_manager = ContextManager()
MAX_TOOL_ITERATIONS = 30


def build_task_context_message():
    task_context = context_manager.get_task_context()

    return types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=(
                    "Here is the current task context. "
                    "Use it to maintain continuity with the user's original task:\n"
                    f"{json.dumps(task_context, indent=2, ensure_ascii=False)}"
                )
            )
        ]
    )

def classify_task(user_message):
    prompt = f"""
    Determine whether the user's latest message is a follow-up
    to the existing task or an entirely new task.

    Existing task:
    {context_manager.original_task}

    Task status:
    {context_manager.task_status}

    Latest user message:
    {user_message}

    Reply with exactly one word:
    FOLLOW_UP
    or
    NEW_TASK
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=10
        )
    )

    return response.text.strip() == "NEW_TASK"

def summarize_oldest_completed_turn():
    completed_turns = conversation_manager.get_completed_turns()

    if not completed_turns:
        return False

    oldest_turn = completed_turns[0]

    turn_text = json.dumps(
        oldest_turn,
        ensure_ascii=False,
        default=lambda obj: (
            obj.model_dump(exclude_none=True)
            if hasattr(obj, "model_dump")
            else str(obj)
        )
    )

    previous_summary = context_manager.conversation_summary

    prompt = f"""
            You are summarizing an AI assistant conversation.

            Previous summary:
            {previous_summary or "No previous summary."}

            Old conversation turn:
            {turn_text}

            Create an updated, concise summary that preserves:
            - The user's requests and goals.
            - Important decisions and explanations.
            - Repository names and file paths.
            - Important findings and conclusions.
            - Unfinished work and pending questions.

            Do not invent information.
            Prioritize information needed to continue the user's task.
            Remove repetition and irrelevant details.
            Keep information needed to continue the conversation.
            """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=600
        )
    )

    new_summary = response.text

    if not new_summary:
        raise ValueError("Gemini failed to generate a conversation summary.")

    # Save the summary before removing the old turn.
    context_manager.update_summary(new_summary)

    conversation_manager.remove_oldest_completed_turn()

    print("Summarized and removed an old conversation turn.")

    return True

def summarize_active_task():
    task_context = context_manager.get_task_context()
    active_turn = conversation_manager.turns[-1]

    turn_text = json.dumps(
        active_turn,
        ensure_ascii=False,
        default=lambda obj: (
            obj.model_dump(exclude_none=True)
            if hasattr(obj, "model_dump")
            else str(obj)
        )
    )

    prompt = f"""
    You are summarizing an active AI assistant task.

    Existing task context:
    {json.dumps(task_context, ensure_ascii=False)}

    Current task messages:
    {turn_text}

    Create an updated task summary that preserves:
    - The original user request.
    - Repository and relevant file paths.
    - Files already inspected.
    - Important findings and evidence.
    - Tool operations already completed.
    - Unfinished work and next steps.

    Do not invent information.
    Do not mark unfinished work as completed.
    Keep the summary concise but sufficiently detailed to continue the task.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=1000
        )
    )

    if not response.text:
        raise ValueError("Gemini failed to summarize the active task.")

    context_manager.update_task_summary(response.text)
    return True

def summarize_and_compact_active_turn():
    active_turn = conversation_manager.get_latest_turn()

    if not active_turn or active_turn["status"] != "in_progress":
        return False

    summarize_active_task()

    conversation_manager.compact_active_turn(active_turn)
    for index, message in enumerate(active_turn["messages"]):
        print(f"\nRemaining message {index + 1}:")

        if hasattr(message, "model_dump"):
            print(
                json.dumps(
                    message.model_dump(exclude_none=True),
                    indent=2,
                    ensure_ascii=False
                )[:3000]
            )
        else:
            print(str(message)[:3000])

    print("Summarized and compacted the active task.")
    print("Messages remaining:", len(active_turn["messages"]))
    print("Task summary characters:", len(context_manager.task_summary))
    print("Conversation summary characters:", len(context_manager.conversation_summary))

    return True

def trim_context():
    previous_token_count = None
    while True:
        tool_definitions = [
            tool.model_dump(exclude_none=True)
            if hasattr(tool, "model_dump")
            else tool
            for tool in GITHUB_TOOLS
        ]

        conversation_messages = conversation_manager.get_messages()
        task_context_message = build_task_context_message()
        count_contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=SYSTEM_INSTRUCTION),
                    types.Part.from_text(
                        text=json.dumps(tool_definitions, ensure_ascii=False)
                    )
                ]
            ),
            task_context_message,
            *conversation_messages
        ]

        token_count = client.models.count_tokens(
            model=MODEL_NAME,
            contents=count_contents
        ).total_tokens

        if previous_token_count is not None:
            if token_count >= previous_token_count:
                raise ValueError(
                    "Context compaction did not reduce token usage."
                )
        print(f"Measured tokens: {token_count}")
        print(f"Conversation turns: {len(conversation_manager.turns)}")
        print(f"Conversation messages: {len(conversation_messages)}")

        if token_count <= CONTEXT_WINDOW:
            print(f"Context usage: {token_count}/{CONTEXT_WINDOW}")
            return

        print("Context window exceeded. Attempting to summarize...")

        summarized = summarize_oldest_completed_turn()

        if not summarized:
            summarized = summarize_and_compact_active_turn()

        if not summarized:
            raise ValueError("Unable to reduce context size.")
        previous_token_count = token_count


def chat_with_assistant(user_message):
    tool_iterations = 0

    if classify_task(user_message):
        context_manager.start_task(user_message)
    turn = conversation_manager.start_turn(user_message)

    try:
        trim_context()

        task_context_message = build_task_context_message()

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                    task_context_message,
                    *conversation_manager.get_messages()
                ],
            config=types.GenerateContentConfig(
                temperature=GENERATION_CONFIG["temperature"],
                tools=GITHUB_TOOLS,
                max_output_tokens=GENERATION_CONFIG["max_output_tokens"],
                system_instruction=SYSTEM_INSTRUCTION
            )
        )

        model_content = response.candidates[0].content
        while tool_iterations < MAX_TOOL_ITERATIONS:
            function_calls = [
                part.function_call
                for part in model_content.parts
                if part.function_call
            ]

            if not function_calls:
                conversation_manager.add_message(
                    turn,
                    model_content.model_dump(exclude_none=True)
                )

                for part in model_content.parts:
                    if part.text:
                        print(part.text)
                context_manager.complete_task()
                conversation_manager.complete_turn(turn)
                break

            tool_iterations += 1

            conversation_manager.add_message(
                turn,
                model_content.model_dump(exclude_none=True)
            )

            function_response_parts = []

            print(f"Function calls in this round: {len(function_calls)}")

            for function_call in function_calls:
                print(f"Tool: {function_call.name}")
                print(f"Arguments: {function_call.args}")

                args = function_call.args
                result = execute_tool(function_call)

                if function_call.name == "get_repository_file":
                    if isinstance(result, dict) and "error" not in result:
                        file_path = args.get("path")

                        if file_path:
                            context_manager.add_inspected_file(file_path)


                if args.get("owner") and args.get("repo"):
                    context_manager.set_repository(
                        args["owner"],
                        args["repo"]
                    )

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

            conversation_manager.add_message(
                turn,
                tool_response_content
            )

            trim_context()
            task_context_message = build_task_context_message()
            
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    task_context_message,
                    *conversation_manager.get_messages()
                ],
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
            conversation_manager.complete_turn(turn)

    except Exception as e:
        print(f"An error occurred while communicating with Gemini: {e}")
        conversation_manager.remove_turn(turn)