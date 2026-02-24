"""Write auto-add JSONL, review queue, and crawl report."""

import json
import os
from datetime import datetime

from .config import DATA_FILE, OUTPUT_DIR
from .entry import EntryCandidate


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def write_auto_add(entries: list[EntryCandidate], data_file: str = DATA_FILE) -> int:
    """Append high-confidence entries to the data JSONL file. Returns count written."""
    if not entries:
        return 0
    with open(data_file, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(entry.to_jsonl() + "\n")
    return len(entries)


def write_review_queue(entries: list[EntryCandidate]) -> int:
    """Write medium-confidence entries to review queue. Returns count written."""
    if not entries:
        return 0
    ensure_output_dir()
    path = os.path.join(OUTPUT_DIR, "review_queue.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries:
            # Include confidence score in the review output
            obj = entry.to_entry_dict()
            obj["_confidence"] = entry.confidence
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return len(entries)


def write_crawl_report(
    auto_added: list[EntryCandidate],
    review: list[EntryCandidate],
    discarded: int,
    skipped_dedup: int,
    targets_processed: int,
    urls_fetched: int,
    errors: list[str],
) -> str:
    """Write a JSON crawl report. Returns the report file path."""
    ensure_output_dir()
    path = os.path.join(OUTPUT_DIR, "crawl_report.json")
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "targets_processed": targets_processed,
            "urls_fetched": urls_fetched,
            "auto_added": len(auto_added),
            "review_queue": len(review),
            "discarded": discarded,
            "skipped_dedup": skipped_dedup,
        },
        "auto_added_entries": [
            {"entity_name": e.entity_name, "source_url": e.source_url,
             "confidence": e.confidence}
            for e in auto_added
        ],
        "review_entries": [
            {"entity_name": e.entity_name, "source_url": e.source_url,
             "confidence": e.confidence}
            for e in review
        ],
        "errors": errors,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return path
