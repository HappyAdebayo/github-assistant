from github_manager import get_repositories, get_repository, list_issues, create_issue, get_issue_details
from schema import RepositoryQuery, RepositoryDetailsQuery, ListIssuesQuery, CreateIssueQuery, GetIssueDetailsQuery

def execute_tool(function_call):
    tool_name = function_call.name
    arguments = function_call.args

    tool_handlers = {
        "get_repositories": lambda: get_repositories(**RepositoryQuery(**arguments).model_dump()),
        "get_repository": lambda: get_repository(**RepositoryDetailsQuery(**arguments).model_dump()),
        "list_issues": lambda: list_issues(**ListIssuesQuery(**arguments).model_dump()),
        "create_issue": lambda: create_issue(**CreateIssueQuery(**arguments).model_dump()),
        "get_issue_details": lambda: get_issue_details(**GetIssueDetailsQuery(**arguments).model_dump()),
    }

    handler = tool_handlers.get(tool_name)

    if handler is None:
        return {
            "success": False,
            "message": f"Unknown tool: {tool_name}"
        }

    try:
        return handler()

    except Exception as e:
        print(f"Unexpected tool execution error: {e}")
        return {
            "success": False,
            "error_type": "internal_error",
            "message": "The GitHub operation could not be completed."
        }