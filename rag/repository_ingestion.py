
from urllib.parse import quote

from github_client import github_request
from github_manager import get_repository
import base64

SUPPORTED_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".md",
    ".mdx",
    ".txt",
    ".sql",
    ".html",
    ".css",
    ".scss",
    ".py",
    ".yaml",
    ".yml",
    ".xml"
}

EXCLUDED_FILENAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml"
}

EXCLUDED_DIRECTORIES = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "coverage",
    "vendor",
    "__pycache__"
}

def get_repository_files(owner, repo):
    """
    Retrieve the file tree of a GitHub repository.
    """

    # Step 1: Get repository information
    repository = get_repository(owner, repo)

    if not isinstance(repository, dict) or "default_branch" not in repository:
        return {"error": f"Could not retrieve repository information: {repository}"}

    default_branch = repository["default_branch"]

    # Step 2: Resolve the latest commit on the default branch
    commit = github_request(
        "GET",
        f"/repos/{owner}/{repo}/commits/{quote(default_branch, safe='')}"
    )

    if not isinstance(commit, dict) or "commit" not in commit:
        return {"error": f"Could not retrieve repository commit: {commit}"}

    tree_sha = commit["commit"]["tree"]["sha"]

    # Step 3: Retrieve the complete Git tree
    tree = github_request(
        "GET",
        f"/repos/{owner}/{repo}/git/trees/{tree_sha}",
        params={"recursive": "1"}
    )

    if not isinstance(tree, dict) or "tree" not in tree:
        return {"error": f"Could not retrieve repository tree: {tree}"}

    # Step 4: Extract files (blobs only)
    files = [
        {
            "path": item["path"],
            "sha": item["sha"],
            "size": item.get("size"),
            "url": item["url"]
        }
        for item in tree["tree"]
        if item["type"] == "blob"
    ]

    return {
        "repository": repository["full_name"],
        "default_branch": default_branch,
        "files": files,
        "total_files": len(files),
        "truncated": tree.get("truncated", False)
    }

def filter_repository_files(files):
    selected_files = []

    for file in files:
        path = file["path"]
        filename = path.split("/")[-1]
        extension = "." + filename.split(".")[-1] if "." in filename else ""

        # Exclude sensitive environment files
        if filename.startswith(".env"):
            continue

        # Exclude lockfiles
        if filename in EXCLUDED_FILENAMES:
            continue

        # Exclude generated and dependency directories
        path_parts = path.split("/")

        if any(directory in EXCLUDED_DIRECTORIES for directory in path_parts):
            continue

        # Only include supported file types
        if extension not in SUPPORTED_EXTENSIONS:
            continue

        selected_files.append(file)

    return selected_files

def extract_file_contents(owner, repo, files):
    documents = []

    for file in files:
        sha = file["sha"]

        result = github_request(
            "GET",
            f"/repos/{owner}/{repo}/git/blobs/{sha}"
        )

        if not isinstance(result, dict) or "content" not in result:
            print(f"Could not retrieve: {file['path']}")
            continue

        content = base64.b64decode(result["content"]).decode("utf-8", errors="replace")

        documents.append({
            "path": file["path"],
            "content": content,
            "sha": sha
        })

    return documents


def get_repository_file(owner, repo, file_path):
    encoded_path = quote(file_path, safe="/")

    result = github_request(
        "GET",
        f"/repos/{owner}/{repo}/contents/{encoded_path}"
    )

    if not isinstance(result, dict):
        return {"error": f"Could not retrieve file: {result}"}

    if result.get("type") != "file":
        return {"error": f"{file_path} is not a file."}

    if "content" not in result:
        return {"error": "GitHub did not return the file contents."}

    if result.get("encoding") != "base64":
        return {"error": "Unsupported file encoding."}

    content = base64.b64decode(result["content"]).decode(
        "utf-8",
        errors="replace"
    )

    return {
        "repository": f"{owner}/{repo}",
        "file_path": file_path,
        "sha": result["sha"],
        "content": content,
        "total_lines": len(content.splitlines())
    }


def search_repository_code(owner, repo, search_term):
    MAX_MATCHES = 40
    MAX_MATCHES_PER_FILE = 10

    result = get_repository_files(owner, repo)

    if not isinstance(result, dict) or "error" in result:
        return result

    selected_files = filter_repository_files(result["files"])
    documents = extract_file_contents(owner, repo, selected_files)

    matches = []
    total_matches = 0

    for document in documents:
        lines = document["content"].splitlines()
        file_matches = 0

        for line_number, line in enumerate(lines, start=1):
            if search_term.lower() in line.lower():
                total_matches += 1

                if (
                    file_matches < MAX_MATCHES_PER_FILE
                    and len(matches) < MAX_MATCHES
                ):
                    matches.append({
                        "file_path": document["path"],
                        "line_number": line_number,
                        "content": line.strip()
                    })
                    file_matches += 1

    return {
        "repository": f"{owner}/{repo}",
        "search_term": search_term,
        "total_matches": total_matches,
        "returned_matches": len(matches),
        "matches": matches,
        "truncated": total_matches > len(matches)
    }
