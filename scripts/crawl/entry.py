"""Entry candidate dataclass and JSONL serialization."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date

from .config import CONTRIBUTOR, TERM_KEY_TO_STRING


@dataclass
class EntryCandidate:
    entity_name: str
    entity_type: str
    country_or_region: str
    terms_found: list[str]  # snake_case keys: chinese_new_year, lunar_new_year, etc.
    exact_phrase: str
    context: str
    platform: str
    source_url: str
    confidence: float = 0.0
    notes: str = ""

    @property
    def dedup_key(self) -> tuple[str, str]:
        return (self.entity_name, self.source_url)

    def term_used(self) -> str | list[str]:
        """Format term_used per schema: string for single, array for multi."""
        if len(self.terms_found) == 1:
            key = self.terms_found[0]
            return TERM_KEY_TO_STRING.get(key, "other")
        return self.terms_found

    def to_entry_dict(self) -> dict:
        """Convert to a schema-valid entry dict."""
        entry = {
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "country_or_region": self.country_or_region,
            "term_used": self.term_used(),
            "exact_phrase": self.exact_phrase,
            "context": self.context,
            "platform": self.platform,
            "sources": [{"url": self.source_url}],
            "captured_on": date.today().isoformat(),
            "contributor": CONTRIBUTOR,
        }
        if self.notes:
            entry["notes"] = self.notes
        return entry

    def to_jsonl(self) -> str:
        """Serialize to a single JSONL line."""
        return json.dumps(self.to_entry_dict(), ensure_ascii=False)
