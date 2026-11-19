from assistant import chat_with_assistant

while True:
    user_question= input("You: ")
    if user_question.lower() == "exit":
        break;

    if not user_question:
        print("Please enter a message: ")
        continue;

    ai_response=chat_with_assistant(user_question)
        

    