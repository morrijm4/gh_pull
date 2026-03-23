import os
import time
from datetime import datetime, timezone
from typing import TypedDict, cast
from urllib.error import HTTPError

from .http import HTTPClient, HTTPResponse


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
    MAX_RATE_LIMIT_RETRIES = 3

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
        res = self.get(
            "/search/code",
            query_params={
                "q": query,
                "page": page,
                "per_page": per_page,
            },
        )

        return cast(CodeSearchResponse, res.json())

    def repo_blobs(self, repo_id: int, sha: str) -> Blob:
        res = self.get(f"/repositories/{repo_id}/git/blobs/{sha}").json()
        return cast(Blob, res)

    def get(self, url: str, query_params: dict | None = None) -> HTTPResponse:
        retries = 0

        while True:
            try:
                return self.http.get(url, query_params=query_params)
            except HTTPError as error:
                if not self._is_rate_limited(error):
                    raise error

                if retries >= self.MAX_RATE_LIMIT_RETRIES:
                    print(error.headers)
                    raise error

                retries += 1
                delay = self._rate_limit_delay_seconds(error)
                print(f"Rate limited {retries}, {delay}")

                if delay > 0:
                    time.sleep(delay)

    def _is_rate_limited(self, error: HTTPError) -> bool:
        if error.code == 429:
            return True

        if error.code != 403:
            return False

        remaining = error.headers.get("x-ratelimit-remaining")
        retry_after = error.headers.get("retry-after")
        return remaining == "0" or retry_after is not None

    def _rate_limit_delay_seconds(self, error: HTTPError) -> float:
        retry_after = error.headers.get("retry-after")
        if retry_after is not None:
            return float(retry_after) + 1

        reset_at = error.headers.get("x-ratelimit-reset")
        if reset_at is None:
            return 60.0

        wait_until = datetime.fromtimestamp(int(reset_at), timezone.utc)
        return max(
            0.0, (wait_until - datetime.now(timezone.utc)).total_seconds() + 2
        )
