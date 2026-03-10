from .item_filter import ItemFilter
from ...utils.result import Result, Ok
from ...clients.github import CodeSearchItem


class PathItemFilter(ItemFilter):
    def filter(self, item: CodeSearchItem) -> Result[bool, str]:
        for fp in self.args.filter_path:
            if fp in item["path"]:
                return Ok(False)
        return Ok(True)
