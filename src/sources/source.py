from abc import ABC, abstractmethod
from typing import Iterable
from ..utils.args import Args
from ..utils.result import Result
from ..engine.search_item import SearchItem


class Source(ABC):
    def __init__(self, args: Args) -> None:
        self.args = args

    @abstractmethod
    def read(self) -> Iterable[Result[tuple[SearchItem, str], str]]:
        raise RuntimeError("Not implimented")
