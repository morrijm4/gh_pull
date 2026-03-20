from pathlib import Path

from .sink import Sink
from ..utils.result import Ok, Err


class DirectorySink(Sink):
    def write(self, item, sample):
        if not self.args.out_dir:
            return Err("Must supply a directory path with --outDir=<DIR_PATH>")

        if self.args.out_dir[-1] != "/":
            self.args.out_dir += "/"

        outputFile: str = (
            self.args.out_dir
            + item.name
            + "/"
            + item.gh["repository"]["name"]
            + "/"
            + item.gh["path"]
        )

        path = Path("/".join(outputFile.split("/")[:-1]))
        path.mkdir(parents=True, exist_ok=True)

        with open(outputFile, "w") as file:
            file.write(sample)

        return Ok()
