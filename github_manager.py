from github_client import github_request

def get_repositories(limit=10, sort="updated", direction="desc"):
    repositories = []
    page = 1

    while len(repositories) < limit:
        per_page = min(limit - len(repositories), 100)
        results = github_request(
            "GET",
            "/user/repos",
            params={
                "visibility": "all",
                "per_page": per_page,
                "sort": sort,
                "page": page,
                "direction": direction
            }
        )

        if not results:
            break

        if isinstance(results, dict) and "error" in results:
            return results

        repositories.extend(results)
        page += 1

    return [
        {
            "id": repo["id"],
            "name": repo["name"],
            "full_name": repo["full_name"],
            "description": repo["description"],
            "private": repo["private"],
            "url": repo["html_url"],
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"],
            "language": repo["language"]
        }
        for repo in repositories[:limit]
]

def get_repository(owner, repo):
    result = github_request(
        "GET",
        f"/repos/{owner}/{repo}"
    )

    return result

def list_issues(owner, repo, state="open", limit=10):
    results = github_request(
        "GET",
        f"/repos/{owner}/{repo}/issues",
        params={
            "state": state,
            "per_page": limit
        }
    )

    return results

def create_issue(owner, repo, title, body=None):
    result = github_request(
        "POST",
        f"/repos/{owner}/{repo}/issues",
        json={
            "title": title,
            "body": body
        }
    )

    return result

def get_issue_details(owner, repo, issue_number):
    result = github_request(
        "GET",
        f"/repos/{owner}/{repo}/issues/{issue_number}"
    )

    return result