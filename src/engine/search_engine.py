from typing import Union
from ..clients.github import CodeSearchItem
from ..utils.args import Args
from ..utils.result import Result, Ok, Err
from ..sinks.sink import Sink
from ..sources.source import Source
from ..filters.code.code_filter import CodeFilter


class SearchEngine:
    def __init__(self, args: Args) -> None:
        self.args = args
        self.sinks: list[Sink] = []
        self.sources: list[Source] = []
        self.code_filters: list[CodeFilter] = []

    def run(self) -> Result[None, str]:
        if len(self.sources) == 0:
            return Err("No source added")
        if len(self.sinks) == 0:
            return Err("Please provide a sink")

        samples: list[tuple[CodeSearchItem, str]] = []

        for src in self.sources:
            res = src.read()

            if res.good():
                samples = [
                    (item, code)
                    for item, code in res.unwrap()
                    if all([f.filter(code).unwrap() for f in self.code_filters])
                ]
            else:
                print(res.unwrap_err())
        print(len(samples))

        for sink in self.sinks:
            for i, sample in enumerate(samples):
                res = sink.write(*sample, i)

                if res.bad():
                    print(res.unwrap_err())

        return Ok()

    def add_sink(self, sink: Union[type[Sink], Sink]):
        self.sinks.append(sink if isinstance(sink, Sink) else sink(self.args))
        return self

    def add_source(self, source: Union[type[Source], Source]):
        self.sources.append(source if isinstance(source, Source) else source(self.args))
        return self

    def add_code_filter(self, f: Union[type[CodeFilter], CodeFilter]):
        self.code_filters.append(f if isinstance(f, CodeFilter) else f(self.args))
        return self
