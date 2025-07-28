"""
Provide access to external Atlus application via CLI.

https://atlus.dev/
https://github.com/whubsch/atlus

Example usage:
```
python scripts/atlusfile.py -f output/ihop.geojson --field "address"
```
"""

import json
import os
import sys
import time
from itertools import batched
from typing import Any, Literal

import requests


from cli_utils import create_geojson_parser, process_input_output_paths


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


def process_file(
    input_path: str, output_path: str, field: Literal["address", "phone"] = "address"
) -> None:
    """
    Process a single GeoJSON file using Atlus request.

    :param input_path: Path to input GeoJSON file
    :param output_path: Path to output processed GeoJSON file
    :param field: Field to process (address or phone)
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Read input file
    with open(input_path, "r") as f:
        content = json.load(f)

    # Process content
    processed_content = atlus_request(content["features"], field)

    content["features"] = processed_content

    # Write processed content
    with open(output_path, "w") as f:
        json.dump(content, f, indent=2)


def process_directory(
    input_dir: str, output_dir: str, field: Literal["address", "phone"] = "address"
) -> None:
    """
    Process all GeoJSON files in a directory.

    :param input_dir: Directory containing input GeoJSON files
    :param output_dir: Directory to save processed GeoJSON files
    :param field: Field to process (address or phone)
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each GeoJSON file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".geojson"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            try:
                process_file(input_path, output_path, field)
                print(f"Processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}", file=sys.stderr)


def main():
    """
    Main CLI entry point for Atlus file processing.
    """
    # Create parser with a specific description
    parser = create_geojson_parser(description="Process GeoJSON files using Atlus API")

    # Field type
    default_field = "address"
    parser.add_argument(
        "--field",
        choices=["address", "phone"],
        default=default_field,
        help=f"Field to process (default: {default_field})",
    )

    # Parse arguments
    args = parser.parse_args()

    # Process input and output paths
    input_path, output_path = process_input_output_paths(args)

    # Determine processing field
    field = args.field

    # Process single file or directory
    if os.path.isfile(input_path):
        process_file(input_path, output_path, field)
        print(f"Processed file saved to: {output_path}")
    else:
        process_directory(input_path, output_path, field)
        print(f"Processed files saved to: {output_path}")


if __name__ == "__main__":
    main()
