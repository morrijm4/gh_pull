from threading import Thread
from queue import Queue
from typing import Union, Optional
from .search_item import SearchItem
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

        source_threads: list[Thread] = []
        sink_threads: list[Thread] = []
        queues: list[Queue[Optional[tuple[SearchItem, str]]]] = []

        for sink in self.sinks:
            q = Queue(maxsize=10)
            queues.append(q)
            t = Thread(target=consumer, args=(sink, q), daemon=True)
            t.start()
            sink_threads.append(t)

        for src in self.sources:
            t = Thread(
                target=producer, args=(src, queues, self.code_filters), daemon=True
            )
            t.start()
            source_threads.append(t)

        for t in source_threads:
            t.join()

        for q in queues:
            q.put(None)

        for t in sink_threads:
            t.join()

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


def producer(
    src: Source,
    queues: list[Queue],
    filters: list[CodeFilter],
):
    for res in src.read():
        if res.bad():
            print(res.unwrap_err())
            break

        item, code = res.unwrap()

        def is_valid() -> bool:
            for f in filters:
                res = f.filter(code)

                if res.bad():
                    print(res.unwrap_err())
                    return False

                if not res.unwrap():
                    return False

            return True

        if not is_valid():
            continue

        for q in queues:
            q.put((item, code))


def consumer(sink: Sink, q: Queue):
    while True:
        item = q.get()
        if item is None:
            break

        try:
            sink.write(*item)
        except Exception as e:
            print(e)
