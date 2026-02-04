import os
import sys
import json
import base64
from collections import defaultdict
from pathlib import Path
from urllib import request


def load_dotenv():
    try:
        with open(".env", "r") as file:
            for line in file:
                key, *value = line.split("=")
                os.environ[key] = "".join(value).removesuffix("\n")
    except Exception:
        pass


def parse_args() -> dict:
    args = defaultdict(list)

    for arg in sys.argv:
        if arg[:2] != "--":
            continue

        key, *value = arg[2:].split("=")
        args[key].append("".join(value) if len(value) > 0 else None)

    for k, v in args.items():
        if len(v) == 1:
            args[k] = v[0]

    return args


def stringify_query_params(qp: dict) -> str:
    return "&".join([f"{k}={v}" for k, v in qp.items()])


def main():
    load_dotenv()

    TOKEN = "GITHUB_TOKEN"
    bearer = os.getenv(TOKEN)

    if bearer is None:
        return print(f"{TOKEN} is not set")

    args = parse_args()

    if "query" not in args or args["query"] is None:
        return print("No query provided with the --query=<QUERY> flag")

    queryParams = {
        "q": "+".join(args["query"])
        if isinstance(args["query"], list)
        else args["query"],
        "page": int(args["page"]) if "page" in args else 1,
        "per_page": int(args["per_page"]) if "per_page" in args else 30,
    }

    url = "https://api.github.com/search/code?" + stringify_query_params(queryParams)
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {bearer}",
    }

    req = request.Request(url, headers=headers)

    items = None
    with request.urlopen(req) as res:
        searchBody = json.loads(res.read().decode())
        items = searchBody["items"]

    if items is None:
        return print("Code not found")

    mode = "output" if "outDir" in args else "interactive"

    totalCount = searchBody["total_count"]
    start = (queryParams["page"] - 1) * queryParams["per_page"]
    end = start + queryParams["per_page"]
    print("Total count:", totalCount)
    print(f"Quering items {start}..{end}")

    if mode == "interactive":
        input("Press ENTER to continue...")

    for i, item in enumerate(items):
        with request.urlopen(item["git_url"]) as res:
            codeBody = json.loads(res.read().decode())

        if codeBody["encoding"] != "base64":
            print(f"Unknown encoding {codeBody['encoding']}")

        code = base64.b64decode(codeBody["content"]).decode()
        currentItem = (i + 1) + start
        repoName = item["repository"]["full_name"]
        filePath = item["path"]
        link = item["html_url"]

        if mode == "output":
            if "outDir" not in args:
                return print("Must supply a directory path with --outDir=<DIR_PATH>")

            if args["outDir"][-1] != "/":
                args["outDir"] += "/"

            outputFile: str = args["outDir"] + repoName + "/" + filePath
            path = Path("/".join(outputFile.split("/")[:-1]))
            path.mkdir(parents=True, exist_ok=True)

            with open(outputFile, "w") as file:
                file.write(code)
        elif mode == "interactive":
            print(code)
            print("Current item", currentItem)
            print("Repository:", repoName)
            print("File path:", filePath)
            print("Link:", link)
            input("Press ENTER to continue...")


if __name__ == "__main__":
    main()
