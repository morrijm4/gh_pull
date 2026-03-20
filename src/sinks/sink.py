from abc import ABC, abstractmethod

from ..engine.search_engine import SearchItem
from ..utils.args import Args
from ..utils.result import Result


class Sink(ABC):
    def __init__(self, args: Args) -> None:
        self.args = args

    @abstractmethod
    def write(self, item: SearchItem, sample: str) -> Result[None, str]:
        raise RuntimeError("Not implimented")
