from abc import ABC, abstractmethod

from ..clients.github import CodeSearchItem
from ..utils.args import Args
from ..utils.result import Result


class Sink(ABC):
    def __init__(self, args: Args) -> None:
        self.args = args

    @abstractmethod
    def write(self, item: CodeSearchItem, sample: str, i: int) -> Result[None, str]:
        raise RuntimeError("Not implimented")
