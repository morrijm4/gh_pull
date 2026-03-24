import os
from pathlib import Path


def load_dotenv():
    try:
        current_file = Path(__file__).resolve()
        with open(current_file.parent.parent / ".env", "r") as file:
            for line in file:
                key, *value = line.split("=")
                os.environ[key] = "".join(value).removesuffix("\n")
    except Exception:
        pass
