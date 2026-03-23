from hashlib import sha256
from threading import Lock

from .code_filter import CodeFilter
from ...engine.search_item import SearchItem
from ...utils.result import Ok, Result


class ContentHashCodeFilter(CodeFilter):
    def __init__(self, args) -> None:
        super().__init__(args)
        self.seen_hashes: set[str] = set()
        self.lock = Lock()

    def filter(self, code: str, item: SearchItem) -> Result[bool, str]:
        digest = sha256(code.encode("utf-8")).hexdigest()

        with self.lock:
            if digest in self.seen_hashes:
                return Ok(False)

            self.seen_hashes.add(digest)

        return Ok(True)
