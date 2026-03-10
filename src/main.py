from .engine.search_engine import SearchEngine
from .utils.args import ArgumentParser
from .utils.load_dotenv import load_dotenv
from .sources.github import GitHubSource
from .sinks.directory import DirectorySink
from .sinks.interactive import InteractiveSink
from .filters.item.path import PathItemFilter
from .filters.code.treesitter import TreesitterCodeFilter


def main():
    load_dotenv()
    args = ArgumentParser().parse()

    if args.bad():
        return print(args.err())
    else:
        args = args.unwrap()

    engine = SearchEngine(args)

    gh = GitHubSource(args)
    gh.add_item_filter(PathItemFilter)

    engine.add_source(gh)
    engine.add_code_filter(TreesitterCodeFilter)

    if args.out_dir:
        engine.add_sink(DirectorySink)
    if args.interactive:
        engine.add_sink(InteractiveSink)

    res = engine.run()

    if res.bad():
        print(res.unwrap_err())
