"""Load and validate targets.yaml into dataclasses."""
from __future__ import annotations

from dataclasses import dataclass, field

import yaml

from .config import TARGETS_PATH


@dataclass
class TargetURL:
    url: str
    context: str = "website"
    platform: str = ""


@dataclass
class Target:
    entity_name: str
    entity_type: str
    country_or_region: str
    urls: list[TargetURL] = field(default_factory=list)
    twitter_handle: str | None = None


def load_targets(path: str = TARGETS_PATH) -> list[Target]:
    """Load targets from a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    targets = []
    for t in data.get("targets", []):
        urls = []
        for u in t.get("urls", []):
            urls.append(TargetURL(
                url=u["url"],
                context=u.get("context", "website"),
                platform=u.get("platform", ""),
            ))
        targets.append(Target(
            entity_name=t["entity_name"],
            entity_type=t["entity_type"],
            country_or_region=t["country_or_region"],
            urls=urls,
            twitter_handle=t.get("twitter_handle"),
        ))
    return targets
