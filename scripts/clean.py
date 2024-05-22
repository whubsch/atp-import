"""
Clean All the Places data in the US and fix most problems. Additional manual review may be needed.
"""

import os
import json
import datetime
import regex
from resources import (
    street_expand,
    direction_expand,
    name_expand,
    useless_tags,
    repeat_tags,
    necessary_tags,
    saints,
)
from atlus import atlus_request
from nsi import (
    nsi_check,
)

VERSION = "0.2.0"

FOLDER_PATH = "./data"

files = [
    os.path.join(root, file)
    for root, _, files in os.walk(FOLDER_PATH)
    for file in files
    if file.startswith("")
    and file.endswith(".geojson")
    and not file.startswith("missing")
]


def get_title(value: str, override_space: bool = False) -> str:
    """Fix ALL-CAPS string."""
    ok = value.isupper() if override_space else value.isupper() and " " in value
    return mc_replace(value.title()) if ok else value


def lower_match(match: regex.Match) -> str:
    """Lower-case improperly cased ordinal values."""
    return match.group(1).lower()


def all_the_same(tags: list[dict], key: str) -> bool:
    """Check if all values of a key are the same."""
    if key in tags:
        return all(item[key] == tags[0][key] for item in tags[1:])
    return False


def us_replace(value: str) -> str:
    """Fix string containing improperly formatted US."""
    return value.replace("U.S.", "US")


def mc_replace(value: str) -> str:
    """Fix string containing improperly formatted Mc- prefix."""
    mc_match = regex.search(r"(.*\bMc)([a-z])(.*)", value)
    if mc_match:
        return mc_match.group(1) + mc_match.group(2).title() + mc_match.group(3)
    return value


def ord_replace(value: str) -> str:
    """Fix string containing improperly capitalized ordinal."""
    return regex.sub(r"(\b[0-9]+[SNRT][tTdDhH]\b)", lower_match, value)


def name_street_expand(match: regex.Match) -> str:
    """Expand matched street type abbreviations."""
    mat = match.group(1).upper().rstrip(".")
    if mat:
        return (name_expand | street_expand)[mat].title()
    raise ValueError


def direct_expand(match: regex.Match) -> str:
    """Expand matched directional abbreviations."""
    mat = match.group(1).upper().replace(".", "")
    if mat:
        return direction_expand[mat].title()
    raise ValueError


# pre-compile regex for speed
abbr_join = "|".join(name_expand | street_expand)
abbr_join_comp = regex.compile(
    rf"(\b(?:{abbr_join})\b\.?)(?!')",
    flags=regex.IGNORECASE,
)

dir_fill = "|".join(r"\.?".join(list(abbr)) for abbr in direction_expand)
dir_fill_comp = regex.compile(
    rf"(?<!(?:^(?:Avenue) |[\.']))(\b(?:{dir_fill})\b\.?)(?!(?:\.?[a-zA-Z]| (?:Street|Avenue)))",
    flags=regex.IGNORECASE,
)

sr_comp = regex.compile(
    r"(\bS\.?R\b\.?)(?= [0-9]+)",
    flags=regex.IGNORECASE,
)

saint_comp = regex.compile(
    rf"^(St\.?)(?= )|(\bSt\.?)(?= (?:{'|'.join(saints)}))",
    flags=regex.IGNORECASE,
)


def get_first(value: str, sep: str = ";") -> str:
    """Return the first value in a semicolon separated string."""
    if ";" in value:
        return get_title(value.split(sep)[0])
    return value


def abbrs(value: str) -> str:
    """Bundle most common abbreviation expansion functions."""
    value = ord_replace(us_replace(mc_replace(value))).replace("  ", " ")

    # change likely 'St' to 'Saint'
    value = saint_comp.sub(
        "Saint",
        value,
    )

    # expand common street and word abbreviations
    value = abbr_join_comp.sub(
        name_street_expand,
        value,
    )

    # expand directionals
    value = dir_fill_comp.sub(
        direct_expand,
        value,
    )

    # expand 'SR' if no other street types
    value = sr_comp.sub("State Route", value)
    return value.strip().replace("  ", " ")


def print_value(action: str, file: str, brand: str, items: int) -> None:
    """Improve console printing for legibility."""
    print(f"{action.title() + '...':<16}{file.split('/')[-1]:<34}{brand:<30}{items:<6}")


def run(file_list: list[str]) -> None:
    """Run the cleaning program on selected files."""
    for file in file_list:
        with open(file, "r", encoding="utf-8") as f:
            contents: dict = json.load(f)

        features = contents["features"]
        clean_data = {
            "version": VERSION,
            "datetime": str(datetime.datetime.now().date()),
        }
        if "dataset_attributes" in contents:
            try:
                if (
                    contents["dataset_attributes"]["cleaning"]["version"] == VERSION
                    or contents["dataset_attributes"]["cleaning"]["status"]
                    == "imported"
                ):
                    print_value(
                        "skipping",
                        file,
                        features[0]["properties"].get("brand"),
                        len(features),
                    )
                    continue
            except KeyError:
                pass
            print_value(
                "processing",
                file,
                features[0]["properties"].get("brand"),
                len(features),
            )
            contents["dataset_attributes"]["cleaning"] = clean_data
        else:
            contents["dataset_attributes"] = {"cleaning": clean_data}

        wipe_repeat_tags: list[str] = []
        for repeat_tag in repeat_tags:
            if all_the_same(features, repeat_tag) and any(
                feature.get(repeat_tag) for feature in features
            ):
                wipe_repeat_tags.append(repeat_tag)

        contents["features"] = atlus_request(features)

        nsi_check(contents)

        for obj in contents["features"]:
            objt: dict[str, str] = obj["properties"]

            if (necessary_tags - set(objt)) == necessary_tags:
                raise ValueError("No top-level tags on object")

            # remove useless ATP-generated tags
            for tag in useless_tags + wipe_repeat_tags:
                objt.pop(tag, None)

            for name_tag in ["name", "branch", "addr:city"]:
                if name_tag in objt:
                    objt[name_tag] = get_first(abbrs(get_title(objt[name_tag])))

            for phone_tag in ["phone", "contact:phone", "fax"]:
                if phone_tag in objt:
                    # split up multiple phone numbers
                    objt.update(
                        {phone_tag: get_first(objt[phone_tag])}
                        if ";" in objt[phone_tag]
                        else {}
                    )

                    # format US and Canada phone numbers
                    phone_valid = regex.search(
                        r"^\(?(?:\+? ?1?[ -.]*)?(?:\(?([0-9]{3})\)?[ -.]*)([0-9]{3})[ -.]*([0-9]{4})$",
                        objt[phone_tag],
                    )
                    phone_perf = regex.search(
                        r"^\+1 [0-9]{3}-[0-9]{3}-[0-9]{4}$", objt[phone_tag]
                    )
                    objt.update(
                        {
                            phone_tag: f"+1 {phone_valid.group(1)}-{phone_valid.group(2)}-{phone_valid.group(3)}"
                        }
                        if phone_valid and not phone_perf
                        else {}
                    )

            for web_tag in ["url", "website", "contact:website"]:
                if web_tag in objt:
                    # check that website uses https
                    if not objt[web_tag].startswith("https:"):
                        raise ValueError("Website does not use HTTPS")

                    # remove url tracking parameters
                    objt[web_tag] = (
                        regex.sub(
                            r"(https?:\/\/[^\s?#]+)(\?)[^#\s]*(utm|cid)[^#\s]*",
                            r"\1",
                            objt[web_tag],
                        )
                        .lower()
                        .replace(" ", "%20")
                    )

            if "addr:postcode" in objt:
                # remove extraneous postcode digits
                objt["addr:postcode"] = regex.sub(
                    r"([0-9]{5})-?0{4}", r"\1", objt["addr:postcode"]
                )

            for ref in [i for i in objt if i.startswith("ref")]:
                # remove refs that are just websites
                if regex.match(
                    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
                    objt[ref],
                ):
                    objt.pop(ref, None)

            for open_hour in [i for i in objt if i.startswith("opening_hours")]:
                open_match = regex.search(r"(\d{2}):\d{2}-\1:\d{2}", objt[open_hour])
                repeat_match = regex.search(
                    r"([MTWFS][ouehra]).*; ?\1", objt[open_hour]
                )
                if open_match or repeat_match:
                    # raise ValueError(
                    #     f"Opening hours [{objt['opening_hours']}] are nonsensical [file: {file}]"
                    # )
                    print(
                        f"Opening hours [{objt['opening_hours']}] are nonsensical [file: {file}]"
                    )

                if "," in objt[open_hour]:
                    op = objt[open_hour].split(";")
                    objt[open_hour] = ";".join([each.split(",")[0] for each in op])
                objt[open_hour] = objt[open_hour].removeprefix("Mo-Su ")

            if objt.get("addr:unit") and objt.get("addr:housenumber"):
                if objt["addr:unit"] == objt["addr:housenumber"]:
                    objt.pop("addr:unit", None)

            obj["properties"] = objt

        with open(file, "w", encoding="utf-8") as f:
            json.dump(contents, f)


if __name__ == "__main__":
    run(files)
