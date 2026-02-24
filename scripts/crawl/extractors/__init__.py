"""Extractor factory."""

from .website import WebsiteExtractor
from .twitter import TwitterExtractor


def get_extractor(source_type: str):
    """Return the appropriate extractor for the given source type."""
    if source_type == "twitter":
        return TwitterExtractor()
    return WebsiteExtractor()
