import os
from typing import TypedDict, cast

from .http import HTTPClient


class Blob(TypedDict):
    encoding: str
    content: str
    sha: str
    size: int
    url: str
    node_id: str


class Repository(TypedDict):
    id: int
    name: str
    full_name: str


class CodeSearchItem(TypedDict):
    score: float
    name: str
    path: str
    sha: str
    url: str
    git_url: str
    html_url: str
    repository: Repository


class CodeSearchResponse(TypedDict):
    total_count: int
    incomplete_results: bool
    items: list[CodeSearchItem]


class GitHubClient:
    def __init__(self, bearer=os.getenv("GITHUB_TOKEN")) -> None:
        if bearer is None:
            raise RuntimeError("GITHUB_TOKEN is not set")

        self.http = HTTPClient(
            "https://api.github.com",
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": f"Bearer {bearer}",
            },
        )

    def code_search(
        self, query: str, page: int = 1, per_page: int = 30
    ) -> CodeSearchResponse:
        res = self.http.get(
            "/search/code",
            query_params={
                "q": query,
                "page": page,
                "per_page": per_page,
            },
        )

        return cast(CodeSearchResponse, res.json())

    def repo_blobs(self, repo_id: int, sha: str) -> Blob:
        res = self.http.get(f"/repositories/{repo_id}/git/blobs/{sha}").json()
        return cast(Blob, res)
