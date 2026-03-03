import os


def load_dotenv():
    try:
        with open(".env", "r") as file:
            for line in file:
                key, *value = line.split("=")
                os.environ[key] = "".join(value).removesuffix("\n")
    except Exception:
        pass
