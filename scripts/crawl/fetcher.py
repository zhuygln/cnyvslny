"""HTTP fetching with disk cache and robots.txt compliance."""
from __future__ import annotations

import hashlib
import logging
import os
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

from .config import CACHE_DIR, REQUEST_TIMEOUT, USER_AGENT
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

# Transient HTTP status codes worth retrying
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_MAX_RETRIES = 2
_RETRY_DELAYS = [3, 6]  # seconds between retries


class Fetcher:
    """Fetches URLs with caching, rate limiting, and robots.txt compliance."""

    def __init__(self, rate_limiter: RateLimiter | None = None,
                 cache_dir: str = CACHE_DIR, use_cache: bool = True):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        self._rate_limiter = rate_limiter or RateLimiter()
        self._cache_dir = cache_dir
        self._use_cache = use_cache
        self._robots_cache: dict[str, RobotFileParser | None] = {}

        if use_cache:
            os.makedirs(cache_dir, exist_ok=True)

    def _cache_path(self, url: str) -> str:
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        return os.path.join(self._cache_dir, f"{url_hash}.html")

    def _check_robots(self, url: str) -> bool:
        """Check if we're allowed to fetch this URL per robots.txt."""
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        if robots_url not in self._robots_cache:
            try:
                resp = self._session.get(robots_url, timeout=(5, 10))
                if resp.status_code == 200:
                    rp = RobotFileParser()
                    rp.parse(resp.text.splitlines())
                    self._robots_cache[robots_url] = rp
                else:
                    self._robots_cache[robots_url] = None
            except Exception:
                # If we can't read robots.txt, assume allowed
                self._robots_cache[robots_url] = None

        rp = self._robots_cache[robots_url]
        if rp is None:
            return True
        return rp.can_fetch(USER_AGENT, url)

    def fetch(self, url: str) -> str | None:
        """Fetch a URL, returning HTML content or None on failure.

        Uses disk cache if available, respects robots.txt and rate limits.
        """
        # Check cache first
        if self._use_cache:
            cache_path = self._cache_path(url)
            if os.path.exists(cache_path):
                logger.debug("Cache hit: %s", url)
                with open(cache_path, "r", encoding="utf-8", errors="replace") as f:
                    return f.read()

        # Check robots.txt
        if not self._check_robots(url):
            logger.info("Blocked by robots.txt: %s", url)
            return None

        # Rate limit
        self._rate_limiter.wait(url)

        # Fetch with retry on transient errors
        resp = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                resp = self._session.get(url, timeout=(5, REQUEST_TIMEOUT), allow_redirects=True)
                if resp.status_code in _RETRYABLE_STATUS_CODES and attempt < _MAX_RETRIES:
                    delay = _RETRY_DELAYS[attempt]
                    logger.info("Retryable %d for %s, waiting %ds (attempt %d/%d)",
                                resp.status_code, url, delay, attempt + 1, _MAX_RETRIES)
                    time.sleep(delay)
                    continue
                resp.raise_for_status()
                break
            except requests.RequestException as e:
                if resp is not None and resp.status_code in _RETRYABLE_STATUS_CODES and attempt < _MAX_RETRIES:
                    delay = _RETRY_DELAYS[attempt]
                    logger.info("Retrying %s after error, waiting %ds (attempt %d/%d)",
                                url, delay, attempt + 1, _MAX_RETRIES)
                    time.sleep(delay)
                    continue
                logger.warning("Fetch failed for %s: %s", url, e)
                return None

        content = resp.text

        # Write to cache
        if self._use_cache:
            cache_path = self._cache_path(url)
            try:
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(content)
            except OSError as e:
                logger.warning("Cache write failed: %s", e)

        return content
