# gh_pull

`gh_pull` is a small Python CLI for collecting real-world C code samples that call specific intrinsics from GitHub code search results.

It queries the GitHub API, downloads matching blobs, filters them down to likely function-level examples, deduplicates them, and writes the surviving files into an output directory organized by intrinsic and repository.

## What It Does

For each intrinsic you provide, the tool:

1. Searches GitHub code search for `<intrinsic> language:c`.
2. Downloads each matching blob through the GitHub API.
3. Rejects duplicate paths that look like the same sample.
4. Parses the C source with Tree-sitter and keeps only functions that:
   - have primitive-typed parameters, and
   - call the requested intrinsic somewhere in the function body.
5. Rejects duplicate file contents using a SHA-256 hash.
6. Writes the remaining samples to disk.

## Repository Layout

- `gh_pull.py`: CLI entrypoint.
- `src/main.py`: wires together the source, filters, and sink.
- `src/sources/github.py`: GitHub code search and blob fetching.
- `src/clients/github.py`: authenticated GitHub API client with basic rate-limit retry handling.
- `src/filters/item/path_dedup.py`: path-based deduplication.
- `src/filters/code/treesitter.py`: AST-based filtering for relevant C functions.
- `src/filters/code/content_hash.py`: content-based deduplication.
- `src/sinks/directory.py`: writes results to the filesystem.

## Requirements

- Python 3.9+
- A GitHub personal access token in `GITHUB_TOKEN`

Python dependencies are listed in `requirements.txt`:

- `tree-sitter`
- `tree-sitter-c`

Install them with:

```sh
python -m pip install -r requirements.txt
```

## Authentication

Set a GitHub token in your environment:

```sh
export GITHUB_TOKEN=your_token_here
```

The project also attempts to load a local `.env` file at startup, so this works too:

```dotenv
GITHUB_TOKEN=your_token_here
```

## Usage

Run the CLI through the repository entrypoint:

```sh
python gh_pull.py --intrinsic=_mm_add_ps --outDir=./out
```

You can supply multiple intrinsics:

```sh
python gh_pull.py \
  --intrinsic=_mm_add_ps \
  --intrinsic=_mm_mul_ps \
  --outDir=./out
```

You can also load intrinsics from a CSV file. The parser expects a `name` column:

```csv
name
_mm_add_ps
_mm_mul_ps
```

```sh
python gh_pull.py --intrinsic_csv_path=./intrinsics.csv --outDir=./out
```

## CLI Arguments

- `--intrinsic=<NAME>`: add one intrinsic to search for. Can be repeated.
- `--intrinsic_csv_path=<PATH>`: load more intrinsic names from a CSV file with a `name` column.
- `--page=<N>`: starting GitHub search results page. Default: `1`.
- `--per_page=<N>`: GitHub page size. Default: `30`. Maximum effective value: `100`.
- `--outDir=<DIR>`: output directory for saved files.
- `--query=<VALUE>`: accepted by the argument parser, but not currently used by the GitHub source.
- `--filterPath=<VALUE>`: accepted by the argument parser, but not currently used anywhere else in the code.

## Output Layout

Files are written under:

```text
<outDir>/<intrinsic>/<repository_name>/<original/path/from/repo>
```

Example:

```text
out/_mm_add_ps/simd-utils/src/math/vector.c
```

## Current Behavior and Limits

- `--outDir` is effectively required in the current implementation.
  `src/main.py` only adds a directory sink, and `SearchEngine.run()` returns an error if no sink is configured.
- GitHub code search is capped at 1,000 results per intrinsic by `GitHubSource.SEARCH_RESULTS_CAP`.
- Only C files are searched because queries are forced to `language:c`.
- Tree-sitter filtering is intentionally narrow and may exclude valid samples if they do not match the expected AST shape.
- Rate limiting is retried a few times in `src/clients/github.py`, but large runs can still take time.

## Example Workflow

```sh
export GITHUB_TOKEN=your_token_here
python -m pip install -r requirements.txt
python gh_pull.py --intrinsic=_mm256_add_epi32 --outDir=./samples
```

Then inspect:

```sh
find ./samples -type f | head
```

## Notes for Development

- The codebase is organized as a small pipeline: `Source -> Item filters -> Code filters -> Sink`.
- Search and sink processing are threaded in `src/engine/search_engine.py`.
- There is currently no stdout or interactive sink, even though the older README implied one existed.
