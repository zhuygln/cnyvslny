"""Abstract base extractor."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ExtractionResult:
    """Result from extracting terms from a single source."""
    terms_found: list[str]       # snake_case keys
    exact_phrase: str             # best matching phrase/snippet
    page_title: str               # page/tweet title
    page_text: str                # full extracted text
    term_count: int               # total term occurrences
    year_relevant: bool           # whether content is from current CNY season


class BaseExtractor(ABC):
    """Abstract base class for term extractors."""

    @abstractmethod
    def extract(self, content: str, url: str) -> ExtractionResult | None:
        """Extract CNY/LNY terms from content.

        Args:
            content: Raw content (HTML for websites, tweet text for Twitter)
            url: Source URL

        Returns:
            ExtractionResult or None if no relevant terms found
        """
        ...
