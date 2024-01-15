import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def export_env():
    ENV_FILE = os.path.join(BASE_DIR, '.env')
    print(f"ENV FILE PATH:\t{ENV_FILE}")
    with open(ENV_FILE) as file:
        for line in file:
            print(f"LINE:\t{line}")
            if line.startswith('##') or line.startswith("#"):
                print("Comment Line.")
                continue
            elif not line.startswith("##"):
                key, value = line.replace('"', "").replace("'", "").strip().split(" = ", 1)
                print(f"KEY: {key}\tVALUE: {value}\n\n")
                os.environ[key] = value
            elif line.startswith("") or line.startswith(" "):
                print("Blank Line.")
                continue


if __name__=="__main__":
    export_env()