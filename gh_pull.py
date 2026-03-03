import base64
from pathlib import Path

from modules import load_dotenv
from modules.argument_parser import ArgumentParser
from clients.http import HTTPClient
from clients.github import GitHubClient


def main():
    load_dotenv()
    args = ArgumentParser().parse()
    github_client = GitHubClient()
    http_client = HTTPClient()

    if args.bad():
        return print(args.err())
    else:
        args = args.unwrap()

    searchBody = github_client.code_search(args.query, args.page, args.per_page)
    items = searchBody["items"]

    if items is None:
        return print("Code not found")

    mode = "output" if args.out_dir else "interactive"

    totalCount = searchBody["total_count"]
    start = (args.page - 1) * args.per_page
    end = start + args.per_page

    print("Total count:", totalCount)
    print(f"Quering items {start}..{end}")

    if mode == "interactive":
        input("Press ENTER to continue...")

    for i, item in enumerate(items):
        currentItem = (i + 1) + start
        repoName = item["repository"]["full_name"]
        filePath = item["path"]
        link = item["html_url"]

        filterItem = False
        for pfilter in args.filter_path:
            if pfilter in filePath:
                filterItem = True
                break
        if filterItem:
            continue

        codeBody = http_client.get(item["git_url"]).json()

        if codeBody["encoding"] != "base64":
            print(f"Unknown encoding {codeBody['encoding']}")

        code = base64.b64decode(codeBody["content"]).decode()

        if mode == "output":
            if args.out_dir is None:
                return print("Must supply a directory path with --outDir=<DIR_PATH>")

            if args.out_dir[-1] != "/":
                args.out_dir += "/"

            outputFile: str = args.out_dir + repoName + "/" + filePath
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
