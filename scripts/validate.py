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

    # Validate sources array
    if "sources" in entry:
        sources = entry["sources"]
        if not isinstance(sources, list):
            errors.append(f"{prefix}: field 'sources' must be an array")
        elif len(sources) < 1:
            errors.append(f"{prefix}: field 'sources' must have at least 1 item")
        else:
            allowed_source_keys = {"url", "evidence"}
            for i, src in enumerate(sources):
                sp = f"{prefix}: sources[{i}]"
                if not isinstance(src, dict):
                    errors.append(f"{sp}: must be an object")
                    continue
                if "url" not in src:
                    errors.append(f"{sp}: missing required field 'url'")
                elif not isinstance(src["url"], str) or not URL_RE.match(src["url"]):
                    errors.append(f"{sp}: 'url' is not a valid URL: '{src.get('url')}'")
                if "evidence" in src and not isinstance(src["evidence"], str):
                    errors.append(f"{sp}: 'evidence' must be a string")
                extra = set(src.keys()) - allowed_source_keys
                if extra:
                    errors.append(f"{sp}: unexpected keys {extra}")


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

                sources = entry.get("sources", [])
                first_url = sources[0]["url"] if sources else None
                dup_key = (entry.get("entity_name"), first_url)
                if dup_key in seen:
                    errors.append(
                        f"{filename}:{line_num}: duplicate entry "
                        f"(entity_name={dup_key[0]!r}, sources[0].url={dup_key[1]!r})"
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
