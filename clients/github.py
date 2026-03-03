import os
from dataclasses import dataclass, field
from typing import Optional

from clients.http import HTTPClient


@dataclass
class GitHubRequestOptions:
    body: Optional[bytes] = None
    query_params: Optional[dict] = None
    method: str = "GET"
    headers: dict = field(default_factory=dict)
    endpoint: str = "/"


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

    def code_search(self, query: str, page: int = 1, per_page: int = 30):
        return self.http.get(
            "/search/code",
            query_params={
                "q": query,
                "page": page,
                "per_page": per_page,
            },
        ).json()
