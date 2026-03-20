import base64
from typing import Iterable, Optional

from .source import Source
from ..clients.http import HTTPClient
from ..clients.github import GitHubClient
from ..engine.search_item import SearchItem
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
        self.query = self.args.query

    def read(self) -> Iterable[Result[tuple[SearchItem, str], str]]:
        for intrinsic in self.args.intrinsics:
            for res in self.fetch_code(intrinsic):
                yield res

    def fetch_code(
        self, intrinsic: str
    ) -> Iterable[Result[tuple[SearchItem, str], str]]:
        i = 0
        j = 0
        page = self.args.page
        per_page = self.args.per_page

        print(f"Fetching code for {intrinsic}")

        while True:
            print(f"{(page - 1) * per_page}..{(page - 1) * per_page + per_page}")
            result = self.gh.code_search(f"{intrinsic}+language:c", page, per_page)

            samples: list[Result[tuple[SearchItem, str], str]] = []
            for gh in result["items"]:
                item = SearchItem(name=intrinsic, gh=gh)

                if not all([i.filter(item).unwrap() for i in self.item_filters]):
                    continue

                blob = self.gh.repo_blobs(gh["repository"]["id"], gh["sha"])
                encoding = blob["encoding"]

                if encoding == "base64":
                    samples.append(
                        Ok((item, base64.b64decode(blob["content"]).decode()))
                    )
                else:
                    return Err(f"Unknown encoding {encoding}.")

            for s in samples:
                yield s

            i += len(result["items"])
            j += len(samples)

            if i >= result["total_count"]:
                break

            page += 1

        print(f"Proccessed {j} items")

    def add_item_filter(self, item_filter: type[ItemFilter]):
        self.item_filters.append(item_filter(self.args))
        return self
