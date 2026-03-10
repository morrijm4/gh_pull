from abc import ABC, abstractmethod
from ...utils.args import Argable
from ...utils.result import Result


class CodeFilter(Argable, ABC):
    @abstractmethod
    def filter(self, code: str) -> Result[bool, str]:
        raise RuntimeError("Not implimented")
