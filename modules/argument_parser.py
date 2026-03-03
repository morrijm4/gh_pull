import sys
from collections import defaultdict
from dataclasses import dataclass
from .result import Ok, Err, Result
from typing import Optional


@dataclass
class Args:
    query: str
    page: int
    per_page: int
    filter_path: list
    out_dir: Optional[str] = None


class ArgumentParser:
    def __init__(self) -> None:
        self.args = defaultdict(list)

        for arg in sys.argv:
            if arg[:2] != "--":
                continue

            key, *value = arg[2:].split("=")
            value = "".join(value) if len(value) > 0 else None
            self.args[key].append(value)

        pass

    def parse(self) -> Result[Args, str]:
        if "query" not in self.args or self.args["query"] is None:
            return Err("No query provided with the --query=<QUERY> flag")

        args = Args(
            query="+".join(self.args["query"]),
            page=int(self.last_or("page", 1)),
            per_page=int(self.last_or("per_page", 30)),
            filter_path=self.args["filterPath"],
            out_dir=self.last("outDir"),
        )

        return Ok(args)

    def last(self, key: str):
        return self.args[key][-1]

    def last_or(self, key: str, default):
        return self.last(key) if key in self.args else default
