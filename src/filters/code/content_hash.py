from hashlib import sha256
from threading import Lock
from collections import defaultdict

from .code_filter import CodeFilter
from ...engine.search_item import SearchItem
from ...utils.result import Ok, Result


class ContentHashCodeFilter(CodeFilter):
    def __init__(self, args) -> None:
        super().__init__(args)
        self.seen_hashes: dict[str, set[str]] = defaultdict(set)
        self.lock = Lock()

    def filter(self, code: str, item: SearchItem) -> Result[bool, str]:
        digest = sha256(code.encode("utf-8")).hexdigest()

        with self.lock:
            seen_hashes = self.seen_hashes[item.name]

            if digest in seen_hashes:
                return Ok(False)

            seen_hashes.add(digest)

        return Ok(True)
