import os
import time
import sys
import json
import base64
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
    args = {}

    for arg in sys.argv:
        if arg[:2] == "--":
            key, *value = arg[2:].split("=")
        else:
            continue

        args[key] = "".join(value) if len(value) > 0 else None

    return args


def make_request(req):
    retries = 0
    while retries < 3:
        try:
            with request.urlopen(req) as res:
                return json.loads(res.read().decode())
        except request.HTTPError as e:
            if e.code == 429 and "Retry-After" in e.headers:
                sleepFor = int(e.headers["Retry-After"])
                print(f"Sleeping for {sleepFor}")
                time.sleep(sleepFor)
            elif (
                e.code == 403
                and e.reason == "rate limit exceeded"
                and e.headers["X-RateLimit-Remaining"] == "0"
            ):
                sleepFor = int(e.headers["X-RateLimit-Reset"]) - time.time()
                print(f"Sleeping for {sleepFor}")
                if sleepFor >= 0:
                    time.sleep(sleepFor)
                else:
                    raise e
        except Exception as e:
            raise e

        retries += 1

    print(f"Failed to make request after {retries}")
    raise RuntimeError


def main():
    load_dotenv()

    TOKEN = "GITHUB_TOKEN"
    bearer = os.getenv(TOKEN)

    if bearer is None:
        return print(f"{TOKEN} is not set")

    args = parse_args()

    if "query" not in args or args["query"] is None:
        return print("No query provided with the -q=<QUERY> flag")

    # _mm512_add_ph+language:c
    url = "https://api.github.com/search/code?q=" + args["query"]
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {bearer}",
    }

    req = request.Request(url, headers=headers)

    items = None
    with request.urlopen(req) as res:
        body = json.loads(res.read().decode())
        items = body["items"]

    if items is None:
        return print("Code not found")

    mode = "output" if "outDir" in args else "interactive"

    for item in items:
        body = make_request(item["git_url"])

        if body["encoding"] != "base64":
            print(f"Unknown encoding {body['encoding']}")

        code = base64.b64decode(body["content"]).decode()
        repoName = item["repository"]["full_name"]
        filePath = item["path"]
        link = item["html_url"]

        if mode == "output":
            if "outDir" not in args:
                return print("Must supply a directory path with -o=<DIR_PATH>")

            if args["outDir"][-1] != "/":
                args["outDir"] += "/"

            outputFile: str = args["outDir"] + repoName + "/" + filePath
            path = Path("/".join(outputFile.split("/")[:-1]))
            path.mkdir(parents=True, exist_ok=True)

            with open(outputFile, "w") as file:
                file.write(code)
        else:
            print(code)
            print("Repository:", repoName)
            print("File path:", filePath)
            print("Link:", link)
            input()


if __name__ == "__main__":
    main()
