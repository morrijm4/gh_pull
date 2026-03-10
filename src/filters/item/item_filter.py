from abc import ABC, abstractmethod
from ...utils.args import Argable
from ...utils.result import Result
from ...clients.github import CodeSearchItem


class ItemFilter(Argable, ABC):
    @abstractmethod
    def filter(self, item: CodeSearchItem) -> Result[bool, str]:
        raise RuntimeError("Not implimented")
