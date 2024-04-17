"""
Provide access to external Atlus application.

https://atlus.dev/
https://github.com/whubsch/atlus
"""

from itertools import batched
import time
from typing import Any

import requests

API_URL = "http://localhost:5000/api/address/batch/"  # live at https://atlus.dev/


def atlus_request(content: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Process address fields using Atlus application."""
    add = []
    for obj in content:
        objt = obj["properties"]

        for addr_tag in ["addr:street_address", "addr:full"]:
            if addr_tag in objt:
                add.append({"@id": obj["id"], "address": objt[addr_tag]})
                continue

    add_chunks = list(batched(add, 10000))
    fin_add = []
    for chunk in add_chunks:
        response = requests.post(API_URL, json=chunk, timeout=10, verify=False)
        fin_add.extend(response.json()["data"])
        if len(fin_add) > 1:
            time.sleep(0.25)

    for i, adds in enumerate(fin_add):
        props = content[i]["properties"]
        if not adds.get("error", None):
            for tag in ["addr:street_address", "addr:full"]:
                props.pop(tag, None)
            for tag in ["@id", "@removed"]:
                adds.pop(tag, None)

            content[i]["properties"] = props | adds
    return content
