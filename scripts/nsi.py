"""Allow checking ATP values against the NSI index."""

from typing import Any
import json
import requests


class AmbiguousValueError(Exception):
    """Declare an ambiguous value error."""

    def __init__(self, message="Ambiguous value encountered."):
        self.message = message
        super().__init__(self.message)


def only_needed(contents: dict) -> dict[Any, Any]:
    """Remove non-used data from NSI json."""
    contents["nsi"] = {
        k: v for k, v in contents["nsi"].items() if k.startswith("brands")
    }

    for v in contents["nsi"].values():
        a = []
        for entry in v["items"]:
            if "us" in entry["locationSet"]["include"] or (
                "001" in entry["locationSet"]["include"]
                and not "us" in entry["locationSet"].get("exclude", [])
            ):
                for rtag in ["id", "locationSet", "fromTemplate"]:
                    entry.pop(rtag, None)
                a.append(entry)
        v["items"] = a
    return contents


def fetch_and_save_nsi_json(url: str, filename: str = "scripts/nsi.json"):
    """Get the latest NSI json file."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = only_needed(response.json())
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
            print("JSON data saved successfully to", filename)
        else:
            print(
                "Failed to fetch JSON data from GitHub. Status code:",
                response.status_code,
            )
    except Exception as e:
        print("An error occurred:", e)


def get_nsi_tags(qwiki: str, base: str, value: str):
    """Get the necessary NSI tags, given a wikidata identifier."""
    with open("scripts/nsi.json", "r", encoding="utf-8") as file:
        contents = json.load(file)
        a = [
            i["tags"]
            for i in contents["nsi"].get(f"brands/{base}/{value}")["items"]
            if i["tags"].get("brand:wikidata", None) == qwiki
        ]
        if len(a) == 1:
            return a[0]
        raise AmbiguousValueError(
            f"Multiple possible NSI entries matching this wikidata: {qwiki}"
        )


def compare_dicts(dict_canon: dict[str, str], dict_new: dict[str, str]) -> bool:
    """Check that the given tags match the NSI canonical."""
    if not all(i in dict_new for i in dict_canon):
        return False

    dict_canon.pop("name", None)
    return all(dict_canon.get(key) == dict_new.get(key) for key in dict_canon)


if __name__ == "__main__":
    github_url = "https://raw.githubusercontent.com/osmlab/name-suggestion-index/main/dist/nsi.json"
    fetch_and_save_nsi_json(github_url)
