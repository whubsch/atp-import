import regex
import os
import json
import datetime
from resources import (
    street_expand,
    direction_expand,
    name_expand,
    useless_tags,
    repeat_tags,
    overlap_tags,
)

version = "0.1.1"

folder_path = "./data"

files = [
    os.path.join(root, file)
    for root, _, files in os.walk(folder_path)
    for file in files
    if file.endswith(".geojson")
]


def get_title(value: str) -> str:
    return value.title() if value.isupper() else value


def all_the_same(tags: list[dict], key: str) -> bool:
    if key in tags:
        return all(item[key] == tags[0][key] for item in tags[1:])
    return False


def us_replace(value: str) -> str:
    if "U.S." in value:
        return value.replace("U.S.", "US")
    return value


def mc_replace(value: str) -> str:
    mc_match = regex.search(r"(.*\bMc)([a-z])(.*)", value)
    if mc_match:
        return mc_match.group(1) + mc_match.group(2).title() + mc_match.group(3)
    return value


def ord_replace(value: str) -> str:
    ord_match = regex.search(r"(\b[0-9]+[SNRT][tTdDhH]\b)", value)
    if ord_match:
        return value.replace(ord_match.group(1), ord_match.group(1).lower())
    return value


for file in files:
    with open(file, "r") as f:
        contents: dict = json.load(f)

    clean_data = {"version": version, "datetime": str(datetime.datetime.now().date())}
    if "dataset_attributes" in contents:
        try:
            if contents["dataset_attributes"]["cleaning"]["version"] == version:
                print(f"Skipping {file}...")
                continue
        except KeyError:
            pass
        print(f"Processing {file}...")
        contents["dataset_attributes"]["cleaning"] = clean_data
    else:
        contents["dataset_attributes"] = {"cleaning": clean_data}

    obj_tags_new: list[dict[str, str | dict]] = []

    wipe_repeat_tags: list[str] = []
    features: list[dict[str, str]] = [
        feature["properties"] for feature in contents["features"]
    ]
    for repeat_tag in repeat_tags:
        if all_the_same(features, repeat_tag) and any(
            feature.get(repeat_tag) for feature in features
        ):
            wipe_repeat_tags.append(repeat_tag)

    for obj in contents["features"]:
        objt: dict[str, str] = obj["properties"]
        # remove useless ATP-generated tags
        for tag in useless_tags + wipe_repeat_tags:
            objt.pop(tag, None)

        for name_tag in ["name", "branch"]:
            if name_tag in objt:
                objt[name_tag] = ord_replace(mc_replace(us_replace(objt[name_tag])))

                # change likely 'St' to 'Saint'
                objt[name_tag] = regex.sub(
                    r"^(St.?)( .+)$", r"Saint\2", objt[name_tag], flags=regex.IGNORECASE
                )
                objt[name_tag] = get_title(objt[name_tag]).replace("  ", " ")

                # expand common street and word abbreviations
                for abbr, replacement in (name_expand | street_expand).items():
                    objt[name_tag] = regex.sub(
                        rf"(\b(?:{abbr})\b\.?)",
                        replacement.title(),
                        objt[name_tag],
                        flags=regex.IGNORECASE,
                    )

                # expand directionals
                for abbr, replacement in direction_expand.items():
                    abbr_fill = r"\.?".join(list(abbr))
                    objt[name_tag] = regex.sub(
                        rf"(?<!(?:^(?:Avenue|Street) |\.))(\b{abbr_fill}\b\.?)(?! (?:Street|Avenue))",
                        replacement,
                        objt[name_tag],
                    )

        for addr_tag in ["addr:street_address", "addr:full"]:
            if addr_tag in objt:
                if all(key in objt for key in {"addr:street", "addr:housenumber"}):
                    objt.pop(addr_tag, None)

                # split up ATP-generated address field
                address_match = regex.match(
                    r"([0-9]+)(?:-?([A-Z]+))? ([a-zA-Z .'0-9]+)",
                    objt[addr_tag],
                )
                if address_match:
                    objt["addr:housenumber"] = address_match.group(1)
                    objt["addr:street"] = (
                        get_title(address_match.group(3)).rstrip().replace("  ", " ")
                    )
                    if address_match.group(2):
                        objt["addr:unit"] = address_match.group(2)
                    objt.pop(addr_tag, None)
                    objt.pop("addr:full", None)
                    break

        if "addr:city" in objt:
            # title-case upper cased cities
            objt["addr:city"] = mc_replace(get_title(objt["addr:city"]))

        if "addr:street" in objt:
            objt["addr:street"] = ord_replace(
                mc_replace(us_replace(objt["addr:street"]))
            )

            # change likely 'St' to 'Saint'
            objt["addr:street"] = regex.sub(
                r"^(St.?)( .+)$", r"Saint\2", objt["addr:street"]
            )
            objt["addr:street"] = regex.sub(
                r"St.?( [NESW]\.?[EW]?\.?)?$", r"Street\1", objt["addr:street"]
            )
            suite_match = regex.search(r"^(St.?)( .+)$", objt["addr:street"])
            if suite_match:
                objt["addr:street"] = suite_match.group(1)
                objt["addr:unit"] = suite_match.group(2)

            # expand common street and word abbreviations
            for abbr, replacement in (name_expand | street_expand).items():
                objt["addr:street"] = regex.sub(
                    rf"(\b(?:{abbr})\b\.?)",
                    replacement.title(),
                    objt["addr:street"],
                    flags=regex.IGNORECASE,
                )

            # expand directionals
            for abbr, replacement in direction_expand.items():
                abbr_fill = r"\.?".join(list(abbr))
                objt["addr:street"] = regex.sub(
                    rf"(?<!(?:^(?:Avenue|Street) |\.))(\b{abbr_fill}\b\.?)(?! (?:Street|Avenue))",
                    replacement,
                    objt["addr:street"],
                )

        if "addr:housenumber" in objt:
            # pull out unit numbers
            unit_match = regex.search(
                r"^([0-9]+)[ -]?([A-Za-z]+)$", objt["addr:housenumber"]
            )
            if unit_match:
                objt["addr:housenumber"] = unit_match.group(1)
                objt["addr:unit"] = unit_match.group(2)

        for phone_tag in ["phone", "contact:phone", "fax"]:
            if phone_tag in objt:
                # split up multiple phone numbers
                if ";" in objt[phone_tag]:
                    objt[phone_tag] = objt[phone_tag].split(";")[0]

                # format US and Canada phone numbers
                phone_valid = regex.search(
                    r"^\(?(?:\+? ?1?[ -.]*)?(?:\(?([0-9]{3})\)?[ -.]*)([0-9]{3})[ -.]*([0-9]{4})$",
                    objt[phone_tag],
                )
                phone_perf = regex.search(
                    r"^\+1 [0-9]{3}-[0-9]{3}-[0-9]{4}$", objt[phone_tag]
                )
                if phone_valid and not phone_perf:
                    objt[
                        phone_tag
                    ] = f"+1 {phone_valid.group(1)}-{phone_valid.group(2)}-{phone_valid.group(3)}"

        for web_tag in ["url", "website", "contact:website"]:
            if web_tag in objt:
                # remove url tracking parameters
                objt[web_tag] = regex.sub(
                    r"(https?:\/\/[^\s?#]+)(\?)[^#\s]*(utm|cid)[^#\s]*",
                    r"\1",
                    objt[web_tag],
                )

        if "addr:postcode" in objt:
            # remove extraneous postcode digits
            objt["addr:postcode"] = regex.sub(
                r"([0-9]{5})-?0{4}", r"\1", objt["addr:postcode"]
            )

        obj["properties"] = objt

    with open(file, "w") as f:
        json.dump(contents, f)
