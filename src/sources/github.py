import base64
from typing import Optional, Union, Self

from .source import Source
from ..clients.http import HTTPClient
from ..clients.github import GitHubClient, CodeSearchItem
from ..utils.args import Args
from ..utils.result import Result, Ok, Err
from ..filters.item.item_filter import ItemFilter


class GitHubSource(Source):
    def __init__(
        self,
        args: Args,
        gh=GitHubClient,
        http=HTTPClient,
        item_filters: Optional[list[ItemFilter]] = None,
    ) -> None:
        super().__init__(args)
        self.gh = gh()
        self.http = http()
        self.item_filters = item_filters or []

        # Source Metadata
        self.total_count = Union[int, None]
        self.incomplete_results = Union[bool, None]

    def read(self) -> Result[list[tuple[CodeSearchItem, str]], str]:
        result = self.gh.code_search(
            self.args.query, self.args.page, self.args.per_page
        )

        # Set Metadata
        self.total_count = result["total_count"]
        self.incomplete_results = result["incomplete_results"]

        samples: list[tuple[CodeSearchItem, str]] = []
        for item in result["items"]:
            if not all([i.filter(item).unwrap() for i in self.item_filters]):
                continue

            blob = self.gh.repo_blobs(item["repository"]["id"], item["sha"])
            encoding = blob["encoding"]

            if encoding == "base64":
                samples.append((item, base64.b64decode(blob["content"]).decode()))
            else:
                return Err(f"Unknown encoding {encoding}.")

        return Ok(samples)

    def show(self) -> None:
        start = (self.args.page - 1) * self.args.per_page
        end = start + self.args.per_page

        print("Total count:", self.total_count)
        print(f"Quering items {start}..{end}")

    def add_item_filter(self, item_filter: type[ItemFilter]) -> Self:
        self.item_filters.append(item_filter(self.args))
        return self
