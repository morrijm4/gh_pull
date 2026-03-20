from .engine.search_engine import SearchEngine
from .utils.args import ArgumentParser
from .utils.load_dotenv import load_dotenv
from .sources.github import GitHubSource
from .sinks.directory import DirectorySink
from .filters.item.path_dedup import PathDedupFilter
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
    gh.add_item_filter(PathDedupFilter)

    engine.add_source(gh)
    engine.add_code_filter(TreesitterCodeFilter)

    if args.out_dir:
        engine.add_sink(DirectorySink)

    res = engine.run()

    if res.bad():
        print(res.unwrap_err())
