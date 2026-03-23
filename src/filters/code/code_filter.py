from abc import ABC, abstractmethod
from ...engine.search_item import SearchItem
from ...utils.args import Argable
from ...utils.result import Result


class CodeFilter(Argable, ABC):
    @abstractmethod
    def filter(self, code: str, item: SearchItem) -> Result[bool, str]:
        raise RuntimeError("Not implimented")
