"""
Centralized CLI argument parsing utilities for ATP import scripts.
"""

import argparse
import os
import sys


def create_geojson_parser(
    description: str = "Process GeoJSON files",
) -> argparse.ArgumentParser:
    """
    Create a standardized argument parser for GeoJSON processing scripts.

    :param description: Description of the script's purpose
    :param default_field: Default processing field
    :return: Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(description=description)

    # Mutually exclusive group for input (file or directory)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-f", "--file", help="Input GeoJSON file to process")
    input_group.add_argument(
        "-d", "--directory", help="Input directory containing GeoJSON files"
    )

    # Output specification
    parser.add_argument(
        "-o",
        "--output",
        help='Output file or directory (default: same as input with "_processed" suffix)',
    )

    return parser


def process_input_output_paths(
    args: argparse.Namespace, input_extension: str = ".geojson"
) -> tuple[str, str]:
    """
    Process and validate input/output paths based on CLI arguments.

    :param args: Parsed arguments
    :param input_extension: Expected file extension
    :return: Tuple of (input_path, output_path)
    """
    input_path = None
    output_path = None

    # Validate and process file input
    if args.file:
        # Validate input file extension
        if not args.file.lower().endswith(input_extension):
            print(f"Error: Input must be a {input_extension} file", file=sys.stderr)
            sys.exit(1)

        input_path = os.path.abspath(args.file)

        # Determine output path
        if args.output:
            output_path = os.path.abspath(args.output)
        else:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_processed{ext}"

    # Validate and process directory input
    elif args.directory:
        input_path = os.path.abspath(args.directory)

        # Validate input directory exists
        if not os.path.isdir(input_path):
            print(
                f"Error: Input directory does not exist: {input_path}", file=sys.stderr
            )
            sys.exit(1)

        # Determine output path
        if args.output:
            output_path = os.path.abspath(args.output)
        else:
            output_path = f"{input_path}_processed"
    else:
        raise ValueError("Input must be a file or directory")

    return input_path, output_path


def main():
    """
    Example usage of the CLI utilities.
    """
    parser = create_geojson_parser()
    args = parser.parse_args()

    input_path, output_path = process_input_output_paths(args)

    print(f"Input path: {input_path}")
    print(f"Output path: {output_path}")
    print(f"Processing field: {args.field}")


if __name__ == "__main__":
    main()
