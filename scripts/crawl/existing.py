"""Load existing data/*.jsonl entries and build a dedup index."""
from __future__ import annotations

import json
import glob
import os

from .config import DATA_DIR


def load_existing_keys(data_dir: str = DATA_DIR) -> set[tuple[str, str]]:
    """Return a set of (entity_name, first_source_url) from all JSONL files."""
    seen: set[tuple[str, str]] = set()
    pattern = os.path.join(data_dir, "*.jsonl")
    for filepath in sorted(glob.glob(pattern)):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                sources = entry.get("sources", [])
                first_url = sources[0]["url"] if sources else ""
                seen.add((entry.get("entity_name", ""), first_url))
    return seen
