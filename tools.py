
from google.genai import types

GET_REPOSITORIES_TOOL = types.FunctionDeclaration(
    name="get_repositories",
    description="""
    Retrieves repositories accessible to the authenticated GitHub user,
    including public and private repositories.

    Use this tool when the user wants to list, view, filter, or sort
    their GitHub repositories.

    The user can specify how many repositories to retrieve and how
    they should be sorted.

    Supported sorting options:
    - created: Repository creation date.
    - updated: Last repository update date.
    - pushed: Last push date.
    - full_name: Repository name.

    Returns repository information such as name, description,
    visibility, URL, default branch, and creation date.
    """,
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "limit": types.Schema(
                type=types.Type.INTEGER,
                description="Maximum number of repositories to return. Defaults to 10."
            ),
            "sort": types.Schema(
                type=types.Type.STRING,
                description="Sort repositories by created, updated, pushed, or full_name. Defaults to updated.",
                enum=["created", "updated", "pushed", "full_name"]
            ),
            "direction": types.Schema(
                type=types.Type.STRING,
                description="Sorting order: asc for oldest first or desc for newest first. Defaults to desc.",
                enum=["asc", "desc"]
            )
        }
    )
)

GET_REPOSITORY_TOOL = types.FunctionDeclaration(
    name="get_repository",
    description="""
    Retrieves detailed information about a specific GitHub repository.

    Use this tool when the user wants to view or inspect a particular
    repository.

    The repository must be identified by its owner and repository name.

    Returns information such as the repository name, description,
    visibility, URL, default branch, creation date, update date,
    programming language, and other repository metadata.
    """,
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "owner": types.Schema(
                type=types.Type.STRING,
                description="The GitHub username or organization that owns the repository."
            ),
            "repo": types.Schema(
                type=types.Type.STRING,
                description="The name of the GitHub repository."
            )
        },
        required=["owner", "repo"]
    )
)

LIST_ISSUES_TOOL = types.FunctionDeclaration(
    name="list_issues",
    description=(
    "Retrieve a list of issues from a specified GitHub repository. "
    "Supports filtering issues by their current state: open, closed, or all. "
    "Use this tool when the user wants to view, browse, or inspect issues "
    "in a repository."
    ),
    parameters={
        "type": "OBJECT",
        "properties": {
            "owner": {
                "type": "STRING",
                "description": "The GitHub username or organization that owns the repository."
            },
            "repo": {
                "type": "STRING",
                "description": "The name of the repository whose issues should be retrieved."
            },
            "state": {
                "type": "STRING",
                "enum": ["open", "closed", "all"],
                "description": "Filter issues by their state. Defaults to open."
            },
            "limit": {
                "type": "INTEGER",
                "description": "Maximum number of issues to retrieve. Defaults to 10."
            }
        },
        "required": ["owner", "repo"]
    }
)

CREATE_ISSUE_TOOL = types.FunctionDeclaration(
    name="create_issue",
    description=(
        "Create a new issue in a specified GitHub repository. "
        "Use this tool when the user explicitly requests to report a bug, "
        "request a feature, or create a task as a GitHub issue."
    ),
    parameters={
        "type": "OBJECT",
        "properties": {
            "owner": {
                "type": "STRING",
                "description": "The GitHub username or organization that owns the repository."
            },
            "repo": {
                "type": "STRING",
                "description": "The name of the repository where the issue should be created."
            },
            "title": {
                "type": "STRING",
                "description": "A clear and concise title describing the issue."
            },
            "body": {
                "type": "STRING",
                "description": "An optional description containing details about the issue."
            }
        },
        "required": ["owner", "repo", "title"]
    }
)

GET_ISSUE_DETAILS_TOOL = types.FunctionDeclaration(
    name="get_issue_details",
    description=(
        "Retrieve detailed information about a specific issue in a GitHub repository. "
        "Use this tool when the user wants to inspect or understand a particular issue. "
        "Returns information such as the issue title, description, state, author, "
        "labels, assignees, and creation date."
    ),
    parameters={
        "type": "OBJECT",
        "properties": {
            "owner": {
                "type": "STRING",
                "description": "The GitHub username or organization that owns the repository."
            },
            "repo": {
                "type": "STRING",
                "description": "The name of the repository containing the issue."
            },
            "issue_number": {
                "type": "INTEGER",
                "description": "The unique issue number assigned by GitHub."
            }
        },
        "required": ["owner", "repo", "issue_number"]
    }
)

GITHUB_TOOLS = [
    types.Tool(
        function_declarations=[GET_REPOSITORIES_TOOL, GET_REPOSITORY_TOOL, LIST_ISSUES_TOOL, CREATE_ISSUE_TOOL,GET_ISSUE_DETAILS_TOOL]
    )
]
