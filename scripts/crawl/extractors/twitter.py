"""Twitter/X API v2 integration via tweepy."""
from __future__ import annotations

import logging
import os
import re

from ..config import TERM_PATTERNS, YEAR_RELEVANCE_PATTERNS
from .base import BaseExtractor, ExtractionResult

logger = logging.getLogger(__name__)

# Lazy import tweepy so the module can be imported without it installed
_tweepy = None


def _get_tweepy():
    global _tweepy
    if _tweepy is None:
        try:
            import tweepy
            _tweepy = tweepy
        except ImportError:
            raise ImportError(
                "tweepy is required for Twitter extraction. "
                "Install it with: pip install tweepy"
            )
    return _tweepy


class TwitterExtractor(BaseExtractor):
    """Extract CNY/LNY terms from Twitter/X via API v2."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client

        token = os.environ.get("TWITTER_BEARER_TOKEN")
        if not token:
            return None

        tweepy = _get_tweepy()
        self._client = tweepy.Client(bearer_token=token, wait_on_rate_limit=True)
        return self._client

    def is_available(self) -> bool:
        """Check if Twitter API is available (bearer token set)."""
        return bool(os.environ.get("TWITTER_BEARER_TOKEN"))

    def search_user_tweets(self, handle: str) -> list[ExtractionResult]:
        """Search a user's recent tweets for CNY/LNY terms.

        Args:
            handle: Twitter handle (with or without @)

        Returns:
            List of ExtractionResults from matching tweets
        """
        client = self._get_client()
        if client is None:
            logger.info("Twitter API not available (no TWITTER_BEARER_TOKEN)")
            return []

        tweepy = _get_tweepy()
        handle = handle.lstrip("@")

        try:
            # Look up user
            user = client.get_user(username=handle)
            if not user.data:
                logger.warning("Twitter user not found: @%s", handle)
                return []

            user_id = user.data.id

            # Get recent tweets (up to 100)
            tweets = client.get_users_tweets(
                user_id,
                max_results=100,
                tweet_fields=["created_at", "text"],
            )

            if not tweets.data:
                return []

        except Exception as e:
            logger.warning("Twitter API error for @%s: %s", handle, e)
            return []

        results = []
        for tweet in tweets.data:
            result = self.extract(tweet.text, f"https://x.com/{handle}/status/{tweet.id}")
            if result:
                results.append(result)

        return results

    def extract(self, content: str, url: str) -> ExtractionResult | None:
        """Extract terms from tweet text."""
        terms_found: dict[str, int] = {}
        total_count = 0

        for key, pattern in TERM_PATTERNS:
            matches = pattern.findall(content)
            if matches:
                terms_found[key] = terms_found.get(key, 0) + len(matches)
                total_count += len(matches)

        if not terms_found:
            return None

        year_relevant = any(
            pat.search(content)
            for pat in YEAR_RELEVANCE_PATTERNS
        )

        return ExtractionResult(
            terms_found=list(terms_found.keys()),
            exact_phrase=content.strip(),
            page_title="",
            page_text=content,
            term_count=total_count,
            year_relevant=year_relevant,
        )
