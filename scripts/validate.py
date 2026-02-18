#!/usr/bin/env python3
"""Validate JSONL data files against the project schema.

Uses only the Python standard library. Exit code 0 on success, 1 on any error.
"""

import json
import glob
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SCHEMA_PATH = os.path.join(ROOT_DIR, "data", "schema.json")
DATA_GLOB = os.path.join(ROOT_DIR, "data", "*.jsonl")

URL_RE = re.compile(r"^https?://\S+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_schema(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_entry(entry, schema, errors, filename, line_num):
    prefix = f"{filename}:{line_num}"

    required = schema.get("required", [])
    properties = schema.get("properties", {})
    allowed_keys = set(properties.keys())

    for field in required:
        if field not in entry:
            errors.append(f"{prefix}: missing required field '{field}'")

    for key in entry:
        if key not in allowed_keys:
            errors.append(f"{prefix}: unexpected field '{key}'")

    for key, value in entry.items():
        if key not in properties:
            continue
        prop = properties[key]

        if prop.get("type") == "string" and not isinstance(value, str):
            errors.append(f"{prefix}: field '{key}' must be a string")
            continue

        if isinstance(value, str):
            if "enum" in prop and value not in prop["enum"]:
                errors.append(
                    f"{prefix}: field '{key}' value '{value}' "
                    f"not in allowed values {prop['enum']}"
                )
            if "minLength" in prop and len(value) < prop["minLength"]:
                errors.append(
                    f"{prefix}: field '{key}' must have at least "
                    f"{prop['minLength']} character(s)"
                )
            if prop.get("format") == "uri" and not URL_RE.match(value):
                errors.append(
                    f"{prefix}: field '{key}' is not a valid URL: '{value}'"
                )
            if prop.get("format") == "date" and not DATE_RE.match(value):
                errors.append(
                    f"{prefix}: field '{key}' is not a valid date "
                    f"(YYYY-MM-DD): '{value}'"
                )


def main():
    if not os.path.exists(SCHEMA_PATH):
        print(f"ERROR: schema not found at {SCHEMA_PATH}", file=sys.stderr)
        sys.exit(1)

    schema = load_schema(SCHEMA_PATH)
    jsonl_files = sorted(glob.glob(DATA_GLOB))

    if not jsonl_files:
        print("WARNING: no JSONL files found in data/")
        sys.exit(0)

    errors = []
    seen = set()

    for filepath in jsonl_files:
        filename = os.path.relpath(filepath, ROOT_DIR)
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"{filename}:{line_num}: invalid JSON: {e}")
                    continue

                validate_entry(entry, schema, errors, filename, line_num)

                dup_key = (entry.get("entity_name"), entry.get("source_url"))
                if dup_key in seen:
                    errors.append(
                        f"{filename}:{line_num}: duplicate entry "
                        f"(entity_name={dup_key[0]!r}, source_url={dup_key[1]!r})"
                    )
                seen.add(dup_key)

    if errors:
        print(f"Validation failed with {len(errors)} error(s):\n", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    total = len(seen)
    print(f"Validation passed: {total} entry/entries across {len(jsonl_files)} file(s).")


if __name__ == "__main__":
    main()
