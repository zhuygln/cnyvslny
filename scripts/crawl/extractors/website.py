"""HTML term extraction using BeautifulSoup."""

import re

from bs4 import BeautifulSoup

from ..config import TERM_PATTERNS, YEAR_RELEVANCE_PATTERNS
from .base import BaseExtractor, ExtractionResult


class WebsiteExtractor(BaseExtractor):
    """Extract CNY/LNY terms from HTML pages."""

    # Tags to strip before text extraction
    STRIP_TAGS = {"script", "style", "nav", "footer", "header", "noscript", "iframe"}

    def extract(self, content: str, url: str) -> ExtractionResult | None:
        soup = BeautifulSoup(content, "lxml")

        # Extract page title
        title_tag = soup.find("title")
        page_title = title_tag.get_text(strip=True) if title_tag else ""

        # Strip boilerplate tags
        for tag in soup.find_all(self.STRIP_TAGS):
            tag.decompose()

        # Extract body text
        body = soup.find("body")
        if body is None:
            page_text = soup.get_text(separator=" ", strip=True)
        else:
            page_text = body.get_text(separator=" ", strip=True)

        # Check year relevance
        year_relevant = any(
            pat.search(page_text) or pat.search(page_title)
            for pat in YEAR_RELEVANCE_PATTERNS
        )

        # Find term matches
        terms_found: dict[str, int] = {}
        total_count = 0
        for key, pattern in TERM_PATTERNS:
            matches = pattern.findall(page_text) + pattern.findall(page_title)
            if matches:
                terms_found[key] = terms_found.get(key, 0) + len(matches)
                total_count += len(matches)

        if not terms_found:
            return None

        # Build exact_phrase: find the best snippet containing a term
        exact_phrase = self._extract_best_phrase(page_text, page_title)

        return ExtractionResult(
            terms_found=list(terms_found.keys()),
            exact_phrase=exact_phrase,
            page_title=page_title,
            page_text=page_text,
            term_count=total_count,
            year_relevant=year_relevant,
        )

    def _extract_best_phrase(self, text: str, title: str) -> str:
        """Extract the best phrase containing a CNY/LNY term.

        Prefers title matches, then sentence-level matches in body text.
        """
        # Check title first
        for _, pattern in TERM_PATTERNS:
            match = pattern.search(title)
            if match:
                return title.strip()

        # Find sentence containing the term in body
        # Split on sentence boundaries
        sentences = re.split(r'[.!?\n]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
            for _, pattern in TERM_PATTERNS:
                if pattern.search(sentence):
                    # Truncate very long sentences
                    if len(sentence) > 200:
                        match = pattern.search(sentence)
                        if match:
                            start = max(0, match.start() - 50)
                            end = min(len(sentence), match.end() + 100)
                            return sentence[start:end].strip()
                    return sentence

        # Fallback: return the first term match with context
        for _, pattern in TERM_PATTERNS:
            match = pattern.search(text)
            if match:
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 70)
                return text[start:end].strip()

        return ""
