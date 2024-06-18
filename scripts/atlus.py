"""
Provide access to external Atlus application.

https://atlus.dev/
https://github.com/whubsch/atlus
"""

from itertools import batched
import time
from typing import Any, Literal

import requests

API_URL = "https://atlus.dev/api/"  # live at https://atlus.dev/


def atlus_request(
    content: list[dict[str, Any]], field: Literal["address", "phone"] = "address"
) -> list[dict[str, Any]]:
    """Process address fields using Atlus application."""
    fields = ["addr:street_address", "addr:full"] if field == "address" else ["phone"]
    add = []
    for obj in content:
        objt = obj["properties"]

        for tag in fields:
            if tag in objt:
                add.append({"@id": obj["id"], "address": objt[tag]})
                break

    add_chunks: list[tuple[dict[str, str]]] = list(batched(add, 10000))
    fin_add = []
    for chunk in add_chunks:
        response = requests.post(
            API_URL + field + "/batch/",
            json=chunk,
            timeout=10,
            verify=bool(API_URL.startswith("https")),
        )
        resp = response.json()
        try:
            fin_add.extend(resp["data"])
        except KeyError as e:
            raise KeyError("Request failed") from e
        if len(fin_add) > 1:
            time.sleep(0.25)

    for i, adds in enumerate(fin_add):
        props = content[i]["properties"]
        if not adds.get("error", None):
            for tag in fields:
                props.pop(tag, None)
            for tag in ["@id", "@removed"]:
                adds.pop(tag, None)

            content[i]["properties"] = props | adds
    return content
