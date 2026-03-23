import sys
import csv
from collections import defaultdict
from dataclasses import dataclass
from .result import Ok, Err, Result
from typing import Optional


@dataclass
class Args:
    intrinsics: list[str]
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
        intrinsics = self.args["intrinsic"]

        if "intrinsic_csv_path" in self.args:
            path = self.last("intrinsic_csv_path")

            with open(path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    intrinsics.append(row["name"])

        if len(intrinsics) == 0:
            return Err(
                "No intrinsics provided. Try the --intrinsic=<STRING> argument or --intrinsic_csv_path=<STRING>"
            )

        args = Args(
            intrinsics=["_mm_aesenc_si128"],
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


class Argable:
    def __init__(self, args: Args) -> None:
        self.args = args
