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

version = "0.1.2"

folder_path = "./data"

files = [
    os.path.join(root, file)
    for root, _, files in os.walk(folder_path)
    for file in files
    if file.endswith(".geojson")
]


def get_title(value: str) -> str:
    return mc_replace(value.title()) if value.isupper() else value


def lower_match(match: regex.Match) -> str:
    return match.group(1).lower()


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
    return regex.sub(r"(\b[0-9]+[SNRT][tTdDhH]\b)", lower_match, value)


def name_street_expand(match: regex.Match) -> str:
    mat = match.group(1).upper().rstrip(".")
    if mat:
        return (name_expand | street_expand)[mat].title()
    raise ValueError


def direct_expand(match: regex.Match) -> str:
    mat = match.group(1).upper().replace(".", "")
    if mat:
        return direction_expand[mat].title()
    raise ValueError


# pre-compile regex for speed
abbr_join = "|".join((name_expand | street_expand).keys())
abbr_join_comp = regex.compile(
    rf"(\b(?:{abbr_join})\b\.?)(?!')",
    flags=regex.IGNORECASE,
)

dir_fill = "|".join([r"\.?".join(list(abbr)) for abbr in direction_expand.keys()])
dir_fill_comp = regex.compile(
    rf"(?<!(?:^(?:Avenue) |[\.']))(\b(?:{dir_fill})\b\.?)(?!(?:\.?[a-zA-Z]| (?:Street|Avenue)))",
    flags=regex.IGNORECASE,
)

sr_comp = regex.compile(
    r"(\bS\.?R\b\.?)(?= [0-9]+)",
    flags=regex.IGNORECASE,
)

saint_comp = regex.compile(r"^(St.?)( .+)$", flags=regex.IGNORECASE)


def get_first(value: str) -> str:
    if ";" in value:
        return get_title(value.split(";")[0])
    return value


def abbrs(value: str) -> str:
    value = ord_replace(us_replace(mc_replace(value))).replace("  ", " ")

    # change likely 'St' to 'Saint'
    value = saint_comp.sub(
        r"Saint\2",
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
    return value.rstrip().lstrip().replace("  ", " ")


def print_value(action: str, file: str, brand: str, items: int):
    print(f"{action.title() + '...':<16}{file.split('/')[-1]:<34}{brand:<30}{items:<6}")


def run() -> None:
    for file in files:
        with open(file, "r") as f:
            contents: dict = json.load(f)

        features = contents["features"]
        clean_data = {
            "version": version,
            "datetime": str(datetime.datetime.now().date()),
        }
        if "dataset_attributes" in contents:
            try:
                if contents["dataset_attributes"]["cleaning"]["version"] == version:
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

        for obj in contents["features"]:
            objt: dict[str, str] = obj["properties"]
            # remove useless ATP-generated tags
            for tag in useless_tags + wipe_repeat_tags:
                objt.pop(tag, None)

            for name_tag in ["name", "branch"]:
                if name_tag in objt:
                    objt[name_tag] = get_first(abbrs(get_title(objt[name_tag])))

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
                        objt["addr:street"] = abbrs(get_title(address_match.group(3)))
                        objt.update(
                            {"addr:unit": address_match.group(2)}
                            if address_match.group(2)
                            else {}
                        )
                        objt.pop(addr_tag, None)
                        objt.pop("addr:full", None)
                        break

            if "addr:city" in objt:
                # process upper cased cities
                objt["addr:city"] = get_first(abbrs(get_title(objt["addr:city"])))

            if "addr:street" in objt:
                street = abbrs(objt["addr:street"])

                street = regex.sub(r"St.?( [NESW]\.?[EW]?\.?)?$", r"Street\1", street)
                suite_match = regex.search(
                    r"(.+?),? (?:(?:S(?:ui)?te|Uni?t|R(?:oo)?m|Apt|Dept|Trlr|Hngr)\.? |#)([A-Z0-9]+)",
                    street,
                    flags=regex.IGNORECASE,
                )
                if suite_match:
                    street = suite_match.group(1)
                    objt["addr:unit"] = suite_match.group(2)

                objt["addr:street"] = street

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
                    # remove url tracking parameters
                    objt[web_tag] = regex.sub(
                        r"(https?:\/\/[^\s?#]+)(\?)[^#\s]*(utm|cid)[^#\s]*",
                        r"\1",
                        objt[web_tag],
                    ).lower()

            if "addr:postcode" in objt:
                # remove extraneous postcode digits
                objt["addr:postcode"] = regex.sub(
                    r"([0-9]{5})-?0{4}", r"\1", objt["addr:postcode"]
                )

            if "ref" in objt:
                # remove refs that are just websites
                if regex.match(
                    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
                    objt["ref"],
                ):
                    objt.pop("ref", None)

            obj["properties"] = objt

        with open(file, "w") as f:
            json.dump(contents, f)


if __name__ == "__main__":
    run()
