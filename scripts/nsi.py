"""Allow checking ATP values against the NSI index."""

import os
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
                and "us" not in entry["locationSet"].get("exclude", [])
            ):
                for rtag in ["id", "locationSet", "fromTemplate"]:
                    entry.pop(rtag, None)
                a.append(entry)
        v["items"] = a
    return contents


def fetch_and_save_nsi_json(url: str, filename: str = "scripts/json/nsi.json"):
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


def get_nsi_tags(qwiki: str, base: str, value: str, brand: str | None):
    """Get the necessary NSI tags, given a wikidata identifier."""
    with open("scripts/json/nsi.json", "r", encoding="utf-8") as file:
        contents = json.load(file)
        tags = [
            i["tags"]
            for i in contents["nsi"].get(f"brands/{base}/{value}")["items"]
            if i["tags"].get("brand:wikidata") == qwiki
        ]

        if not tags:
            raise ValueError(f"No NSI entries matching this wikidata: {qwiki}")
        if len(tags) == 1:
            return tags[0]
        filt = [i for i in tags if i.get("brand") == brand]
        if len(filt) == 1 and brand:
            return filt[0]
        raise AmbiguousValueError(
            f"Multiple possible NSI entries matching this wikidata: {qwiki}"
        )


def compare_dicts(
    dict_canon: dict[str, str], dict_new: dict[str, str]
) -> dict[str, dict[str, str | None]]:
    """Check that the given tags match the NSI canonical."""
    dict_canon.pop("name", None)
    return {
        key: {"nsi": dict_canon.get(key), "atp": dict_new.get(key)}
        for key in dict_canon
        if dict_canon.get(key) != dict_new.get(key)
    }


def get_primary_kv(tags: dict[str, str]) -> tuple[str, str]:
    """Get the object's primary tag and its value."""
    for i in ["amenity", "shop", "tourism", "leisure", "craft", "office", "healthcare"]:
        if i in tags:
            return i, tags[i]
    raise ValueError(f"No primary tags found: {tags}")


def nsi_check(contents: dict, file: str = "") -> None:
    """Check ATP objects vs NSI."""
    first = contents["features"][0]["properties"]
    try:
        k, v = get_primary_kv(first)
        try:
            if first.get("brand:wikidata"):
                canon = get_nsi_tags(
                    first.get("brand:wikidata"), k, v, brand=first.get("brand")
                )
                compare = compare_dicts(canon, first)
                if compare != {}:
                    print()
                    for k, v in compare.items():
                        print(
                            f"| {file.split('/')[-1]} | {first.get('brand')} | {first.get('brand:wikidata')} | {k} | {v.get('nsi')} | {v.get('atp')} |"
                        )
        except AmbiguousValueError as e:
            print(e, "|", first.get("brand"))
        except TypeError:
            pass

    except ValueError:
        pass


def run_check() -> None:
    FOLDER_PATH = "/Users/will/Downloads/output"

    files = [
        os.path.join(root, file)
        for root, _, files in os.walk(FOLDER_PATH)
        for file in files
        if file.startswith("")
        and file.endswith(".geojson")
        and not file.startswith("missing")
    ]
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            try:
                contents: dict = json.load(f)
            except json.decoder.JSONDecodeError:
                continue
            nsi_check(contents, file)


if __name__ == "__main__":
    # GITHUB_URL = "https://raw.githubusercontent.com/osmlab/name-suggestion-index/main/dist/nsi.json"
    # fetch_and_save_nsi_json(GITHUB_URL)
    run_check()
