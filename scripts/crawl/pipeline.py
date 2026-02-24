"""Orchestration: fetch → extract → score → output."""

import json
import logging
import os
import re

from .config import (
    AUTO_ADD_THRESHOLD, DATA_FILE, REVIEW_THRESHOLD, SCHEMA_PATH,
    TERM_KEY_TO_STRING,
)
from .entry import EntryCandidate
from .existing import load_existing_keys
from .extractors import get_extractor
from .extractors.twitter import TwitterExtractor
from .fetcher import Fetcher
from .output import write_auto_add, write_crawl_report, write_review_queue
from .rate_limiter import RateLimiter
from .scoring import score_candidate
from .targets import Target, load_targets

logger = logging.getLogger(__name__)

# Minimal schema validation (mirrors validate.py checks)
URL_RE = re.compile(r"^https?://\S+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

VALID_ENTITY_TYPES = {"company", "school", "gov", "media", "nonprofit", "app", "other"}
VALID_CONTEXTS = {"social_post", "press_release", "product_ui", "email",
                  "event_page", "website", "other"}
VALID_TERM_STRINGS = {"Chinese New Year", "Lunar New Year", "Spring Festival", "other"}
VALID_TERM_ARRAY_ITEMS = {"chinese_new_year", "lunar_new_year", "spring_festival", "other"}


def validate_entry_dict(entry: dict) -> list[str]:
    """Validate an entry dict against the schema. Returns list of errors."""
    errors = []
    required = ["entity_name", "entity_type", "country_or_region", "term_used",
                 "exact_phrase", "context", "platform", "sources", "captured_on",
                 "contributor"]

    for field in required:
        if field not in entry:
            errors.append(f"missing required field '{field}'")

    if entry.get("entity_type") not in VALID_ENTITY_TYPES:
        errors.append(f"invalid entity_type: {entry.get('entity_type')}")

    if entry.get("context") not in VALID_CONTEXTS:
        errors.append(f"invalid context: {entry.get('context')}")

    term = entry.get("term_used")
    if isinstance(term, str) and term not in VALID_TERM_STRINGS:
        errors.append(f"invalid term_used string: {term}")
    elif isinstance(term, list):
        for item in term:
            if item not in VALID_TERM_ARRAY_ITEMS:
                errors.append(f"invalid term_used array item: {item}")

    sources = entry.get("sources", [])
    if not isinstance(sources, list) or len(sources) < 1:
        errors.append("sources must be a non-empty array")
    else:
        for src in sources:
            if "url" not in src:
                errors.append("source missing url")
            elif not URL_RE.match(src["url"]):
                errors.append(f"invalid source url: {src['url']}")

    captured = entry.get("captured_on", "")
    if not DATE_RE.match(captured):
        errors.append(f"invalid captured_on date: {captured}")

    for field in ("entity_name", "platform", "exact_phrase", "contributor"):
        val = entry.get(field, "")
        if isinstance(val, str) and len(val) < 1:
            errors.append(f"field '{field}' must be non-empty")

    return errors


def run_pipeline(
    targets_path: str | None = None,
    entity_filter: str | None = None,
    web_only: bool = False,
    twitter_only: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
    max_targets: int | None = None,
    auto_threshold: float = AUTO_ADD_THRESHOLD,
    review_threshold: float = REVIEW_THRESHOLD,
) -> dict:
    """Run the full crawl pipeline.

    Returns a summary dict with counts.
    """
    # Load targets
    path = targets_path or None
    targets = load_targets(path) if path else load_targets()

    # Filter by entity name if specified
    if entity_filter:
        entity_lower = entity_filter.lower()
        targets = [t for t in targets if entity_lower in t.entity_name.lower()]
        if not targets:
            logger.warning("No targets matching '%s'", entity_filter)
            return {"error": f"No targets matching '{entity_filter}'"}

    # Limit targets
    if max_targets is not None:
        targets = targets[:max_targets]

    logger.info("Processing %d target(s)", len(targets))

    # Load existing entries for dedup
    existing_keys = load_existing_keys()
    logger.info("Loaded %d existing entries for dedup", len(existing_keys))

    # Initialize components
    rate_limiter = RateLimiter()
    fetcher = Fetcher(rate_limiter=rate_limiter)
    website_extractor = get_extractor("website")
    twitter_extractor = TwitterExtractor()

    # Collect results
    auto_add: list[EntryCandidate] = []
    review: list[EntryCandidate] = []
    discarded = 0
    skipped_dedup = 0
    urls_fetched = 0
    errors: list[str] = []

    for target in targets:
        logger.info("Processing: %s", target.entity_name)

        # --- Website URLs ---
        if not twitter_only:
            for target_url in target.urls:
                url = target_url.url
                logger.debug("  Fetching: %s", url)

                html = fetcher.fetch(url)
                urls_fetched += 1

                if html is None:
                    errors.append(f"Failed to fetch: {url}")
                    continue

                result = website_extractor.extract(html, url)
                if result is None:
                    logger.debug("  No terms found: %s", url)
                    continue

                if not result.year_relevant:
                    logger.debug("  Not year-relevant: %s", url)
                    # Still process but note it — recency scoring handles the penalty
                    pass

                candidate = EntryCandidate(
                    entity_name=target.entity_name,
                    entity_type=target.entity_type,
                    country_or_region=target.country_or_region,
                    terms_found=result.terms_found,
                    exact_phrase=result.exact_phrase,
                    context=target_url.context,
                    platform=target_url.platform,
                    source_url=url,
                    notes=f"Auto-crawled from {target_url.platform}",
                )

                # Dedup check
                if candidate.dedup_key in existing_keys:
                    logger.debug("  Skipping duplicate: %s", url)
                    skipped_dedup += 1
                    continue

                # Score
                confidence = score_candidate(
                    candidate,
                    page_title=result.page_title,
                    page_text=result.page_text,
                    term_count=result.term_count,
                )
                candidate.confidence = confidence
                logger.info("  Score %.3f for %s (%s)",
                            confidence, target.entity_name, url)

                # Route
                if confidence >= auto_threshold:
                    auto_add.append(candidate)
                elif confidence >= review_threshold:
                    review.append(candidate)
                else:
                    discarded += 1
                    logger.debug("  Discarded (score %.3f): %s", confidence, url)

        # --- Twitter ---
        if not web_only and target.twitter_handle and twitter_extractor.is_available():
            logger.info("  Searching Twitter: %s", target.twitter_handle)
            try:
                tweet_results = twitter_extractor.search_user_tweets(target.twitter_handle)
                for result in tweet_results:
                    candidate = EntryCandidate(
                        entity_name=target.entity_name,
                        entity_type=target.entity_type,
                        country_or_region=target.country_or_region,
                        terms_found=result.terms_found,
                        exact_phrase=result.exact_phrase,
                        context="social_post",
                        platform="X",
                        source_url=f"https://x.com/{target.twitter_handle.lstrip('@')}",
                        notes="Auto-crawled from Twitter/X",
                    )

                    if candidate.dedup_key in existing_keys:
                        skipped_dedup += 1
                        continue

                    confidence = score_candidate(
                        candidate,
                        page_title="",
                        page_text=result.page_text,
                        term_count=result.term_count,
                    )
                    candidate.confidence = confidence

                    if confidence >= auto_threshold:
                        auto_add.append(candidate)
                    elif confidence >= review_threshold:
                        review.append(candidate)
                    else:
                        discarded += 1
            except Exception as e:
                errors.append(f"Twitter error for {target.twitter_handle}: {e}")

    # Validate auto-add entries; demote invalid ones to review
    validated_auto: list[EntryCandidate] = []
    for candidate in auto_add:
        entry_dict = candidate.to_entry_dict()
        validation_errors = validate_entry_dict(entry_dict)
        if validation_errors:
            logger.warning("Validation failed for %s, demoting to review: %s",
                           candidate.entity_name, validation_errors)
            candidate.notes += f" [validation errors: {'; '.join(validation_errors)}]"
            review.append(candidate)
        else:
            validated_auto.append(candidate)

    # Write output
    if dry_run:
        logger.info("DRY RUN — not writing any files")
        for c in validated_auto:
            logger.info("  [auto-add] %.3f %s — %s",
                        c.confidence, c.entity_name, c.source_url)
        for c in review:
            logger.info("  [review]   %.3f %s — %s",
                        c.confidence, c.entity_name, c.source_url)
    else:
        added = write_auto_add(validated_auto)
        queued = write_review_queue(review)
        # Add newly written entries to dedup set
        for c in validated_auto:
            existing_keys.add(c.dedup_key)
        logger.info("Auto-added %d entries, queued %d for review", added, queued)

    report_path = write_crawl_report(
        auto_added=validated_auto,
        review=review,
        discarded=discarded,
        skipped_dedup=skipped_dedup,
        targets_processed=len(targets),
        urls_fetched=urls_fetched,
        errors=errors,
    )
    logger.info("Crawl report: %s", report_path)

    return {
        "targets_processed": len(targets),
        "urls_fetched": urls_fetched,
        "auto_added": len(validated_auto),
        "review_queue": len(review),
        "discarded": discarded,
        "skipped_dedup": skipped_dedup,
        "errors": errors,
    }
