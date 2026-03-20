from abc import ABC, abstractmethod
from ...utils.args import Argable
from ...utils.result import Result
from ...engine.search_item import SearchItem


class ItemFilter(Argable, ABC):
    @abstractmethod
    def filter(self, item: SearchItem) -> Result[bool, str]:
        raise RuntimeError("Not implimented")
