# gh_pull

## Dependencies

Must supply a GitHub personal access token through the environment variable
`GITHUB_TOKEN`. Optionally, you can supply through a `.env` file.

- python >= 3.9

## Usage

```sh
python gh_pull.py --query=<GITHUB-SEARCH-SYNTAX>
```

Defaults to interactively paging through results (press ENTER for next).
Optionally, provide the `--outDir=<DIR>` flag to save results to a output
directory.
