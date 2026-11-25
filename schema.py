from pydantic import BaseModel, Field
from typing import Literal

class RepositoryQuery(BaseModel):
    limit: int = Field(default=10,ge=1,le=1000,description="Maximum number of repositories to retrieve")
    sort: Literal[ "created", "updated", "pushed", "full_name"] = "updated"
    direction: Literal[ "asc", "desc" ] = "desc"

class RepositoryDetailsQuery(BaseModel):
    owner: str
    repo: str

class ListIssuesQuery(BaseModel):
    owner: str
    repo: str
    state: Literal["open", "closed", "all"] = "open"
    limit: int = Field(default=10, ge=1, le=100)

class CreateIssueQuery(BaseModel):
    owner: str
    repo: str
    title: str
    body: str | None = None

class GetIssueDetailsQuery(BaseModel):
    owner: str
    repo: str
    issue_number: int = Field(ge=1)

class RepositoryQuestionQuery(BaseModel):
    owner: str
    repo: str
    question: str = Field(
        min_length=1,
        description="Question about the repository's code or documentation"
    )

class RepositoryFileQuery(BaseModel):
    owner: str
    repo: str
    file_path: str = Field(
        min_length=1,
        description="Path to the file inside the repository"
    )

class RepositoryCodeSearchQuery(BaseModel):
    owner: str
    repo: str
    search_term: str = Field(
        min_length=1,
        description="Keyword or code pattern to search for"
    )