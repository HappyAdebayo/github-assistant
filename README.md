# GitHub AI Assistant

A Python-based AI assistant powered by Google's Gemini API that interacts with GitHub through function calling. It understands natural-language requests and executes GitHub operations using the GitHub REST API.

## Features

- **List repositories:** Retrieve repositories belonging to the authenticated GitHub user.
- **Get repository details:** Retrieve information about a specific repository.
- **List issues:** Retrieve open, closed, or all issues in a repository.
- **Create issues:** Create GitHub issues using a title and optional description.
- **Get issue details:** Retrieve information about a specific issue.
- **Function calling:** Gemini determines which GitHub tools are needed based on the user's request.
- **Sequential tool execution:** Supports multiple rounds of tool calls to complete tasks that require several operations.
- **Conversation history:** Maintains conversation context across interactions.
- **Context management:** Uses Gemini token counting to monitor context usage and remove older conversation turns when necessary.
- **Input validation:** Uses Pydantic schemas to validate tool arguments before execution.
- **Error handling:** Handles API errors and unexpected tool execution failures.

## Tech Stack

- Python
- Google Gemini API
- Google Gen AI SDK
- GitHub REST API
- Requests
- Pydantic
- python-dotenv

## Project Structure

```text
github-assistant/
│
├── main.py
├── assistant.py
├── config.py
├── prompt.py
├── tools.py
├── tool_executor.py
├── schema.py
├── github_client.py
├── github_manager.py
├── .env
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/github-assistant.git
cd github-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Linux/macOS**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install google-genai python-dotenv requests pydantic
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_personal_access_token
MAX_RETRIES=3
CONTEXT_WINDOW=3000
```

Use a GitHub token with the repository permissions required for the operations you want to perform. Keep your API keys and tokens private.

### 5. Run the assistant

```bash
python main.py
```

## Example Requests

```text
List all my repositories.

Show me the details of my ai_chatbot repository.

List all open issues in ai_chatbot.

Create an issue in ai_chatbot titled "Fix authentication bug".

Get the details of issue number 5 in ai_chatbot.
```

## How It Works

1. The user sends a natural-language request.
2. Gemini interprets the request and decides whether a GitHub tool is needed.
3. Gemini generates a function call with the required arguments.
4. The tool executor validates the arguments using Pydantic.
5. The corresponding Python function interacts with the GitHub REST API.
6. The result is returned to Gemini.
7. Gemini processes the result and generates a response for the user.

The assistant supports multiple rounds of function calling, allowing it to retrieve information and perform subsequent operations when necessary.

## Future Improvements

- Retrieval-Augmented Generation (RAG) for repository knowledge.
- Agentic workflows for more complex GitHub tasks.
- Evaluation and observability.
- Persistent conversation storage.
- Production deployment.

---

**Note:** This project is being developed as a practical exploration of AI engineering, particularly LLM integration, function calling, tool orchestration, and context management.