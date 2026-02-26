"""5-factor confidence scoring for entry candidates."""

import re
from urllib.parse import urlparse

from .entry import EntryCandidate


def score_candidate(candidate: EntryCandidate, page_title: str = "",
                    page_text: str = "", term_count: int = 1) -> float:
    """Score a candidate on 5 factors (max 1.0).

    Factors:
        - Term clarity (0-0.30): term in title? multiple occurrences?
        - Source quality (0-0.25): first-party domain? HTTPS?
        - Recency (0-0.15): year relevance (2025/2026)?
        - Entity match (0-0.15): entity name found on page?
        - Context richness (0-0.15): exact_phrase length/quality?
    """
    score = 0.0

    # 1. Term clarity (max 0.30)
    term_clarity = 0.0
    if term_count >= 1:
        term_clarity += 0.10
    if term_count >= 3:
        term_clarity += 0.10
    # Check if term appears in page title
    for term in ("Chinese New Year", "Lunar New Year", "Spring Festival", "春节"):
        if term.lower() in page_title.lower():
            term_clarity += 0.10
            break
    score += min(term_clarity, 0.30)

    # 2. Source quality (max 0.25)
    source_quality = 0.0
    url = candidate.source_url
    parsed = urlparse(url)
    if parsed.scheme == "https":
        source_quality += 0.05
    # First-party: platform domain matches source URL domain
    platform_domain = candidate.platform.lower().replace("www.", "")
    source_domain = parsed.netloc.lower().replace("www.", "")
    if platform_domain and platform_domain in source_domain:
        source_quality += 0.15
    else:
        source_quality += 0.05  # third-party source
    # Known reputable domains
    reputable = (".gov", ".edu", ".org", ".ac.uk")
    if any(source_domain.endswith(r) for r in reputable):
        source_quality += 0.05
    score += min(source_quality, 0.25)

    # 3. Recency (max 0.15)
    recency = 0.0
    year_patterns = (r"202[56]", r"Year\s+of\s+the\s+(Horse|Snake)")
    for pat in year_patterns:
        if re.search(pat, page_text, re.IGNORECASE):
            recency += 0.10
            break
    # Check captured_on or page content for current season
    if re.search(r"2026", page_text):
        recency += 0.05
    score += min(recency, 0.15)

    # 4. Entity match (max 0.15)
    entity_match = 0.0
    entity_lower = candidate.entity_name.lower()
    if entity_lower in page_text.lower():
        entity_match += 0.15
    elif len(entity_lower) > 3 and any(
        word in page_text.lower() for word in entity_lower.split()
        if len(word) > 3
    ):
        entity_match += 0.08
    score += min(entity_match, 0.15)

    # 5. Context richness (max 0.15)
    context_richness = 0.0
    phrase_len = len(candidate.exact_phrase)
    if phrase_len >= 10:
        context_richness += 0.05
    if phrase_len >= 30:
        context_richness += 0.05
    if phrase_len >= 50:
        context_richness += 0.05
    score += min(context_richness, 0.15)

    return round(min(score, 1.0), 3)
