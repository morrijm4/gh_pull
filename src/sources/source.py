from abc import ABC, abstractmethod
from ..utils.args import Args
from ..utils.result import Result
from ..clients.github import CodeSearchItem


class Source(ABC):
    def __init__(self, args: Args) -> None:
        self.args = args

    @abstractmethod
    def read(self) -> Result[list[tuple[CodeSearchItem, str]], str]:
        raise RuntimeError("Not implimented")

    @abstractmethod
    def show(self) -> None:
        pass
