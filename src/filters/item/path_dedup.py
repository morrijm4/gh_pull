from .item_filter import ItemFilter
from ...utils.result import Result, Ok
from ...engine.search_item import SearchItem


class PathDedupFilter(ItemFilter):
    def __init__(self, args) -> None:
        super().__init__(args)
        self.seen = set()

    def filter(self, item: SearchItem) -> Result[bool, str]:
        path = item.gh["repository"]["full_name"] + "/" + item.gh["path"]
        key = "-".join(path.split("/")[-3:])  # Make key from last 3 filename/dirname

        if key in self.seen:
            return Ok(False)

        self.seen.add(key)
        return Ok(True)
