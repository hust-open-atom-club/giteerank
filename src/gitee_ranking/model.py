from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str
    created_at: int


class Contributor(BaseModel):
    email: str


class Repo(BaseModel):
    issues_count: int = 0
    prs_count: int = 0
    commits_count: int = 0
    contributors_count: int = 0

    contributors: list[Contributor] = []


class Group(BaseModel):
    name: str
    owner: str
    repo: str
    url: str
