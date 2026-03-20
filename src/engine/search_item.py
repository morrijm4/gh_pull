from dataclasses import dataclass
from ..clients.github import CodeSearchItem


@dataclass
class SearchItem:
    gh: CodeSearchItem
    name: str
