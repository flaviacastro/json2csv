#!/usr/bin/env python3

import argparse
import csv
from typing import Any, TypeAlias

import requests

JSONDict: TypeAlias = dict[str, Any]
JSONArray: TypeAlias = list[JSONDict]


def fetch_json(url: str, auth: str = None) -> JSONDict | JSONArray:
    headers = {"Content-Type": "application/json"}

    if auth:
        headers["Authorization"] = auth

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def flatten_dict(d: JSONDict, parent_key: str = "", sep: str = ".") -> JSONDict:
    items = []

    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))

    return dict(items)


def json_to_csv(data: JSONDict | JSONArray, output_file: str) -> None:
    if not isinstance(data, list):
        data = [data]

    flattened = [flatten_dict(item) for item in data]

    keys = []

    for record in flattened:
        keys.extend(record.keys())

    fieldnames = sorted(set(keys))

    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened)

    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert JSON API response to CSV.")

    parser.add_argument("--url", required=True, help="API URL to fetch JSON data from")
    parser.add_argument(
        "--auth", help="Authorization header value (e.g., Bearer TOKEN)"
    )
    parser.add_argument("--output", default="output.csv", help="Output CSV file name")
    
    args = parser.parse_args()
    data = fetch_json(args.url, args.auth)
    json_to_csv(data, args.output)
    print(f"CSV file created: {args.output}")

    return None


if __name__ == "__main__":
    main()
