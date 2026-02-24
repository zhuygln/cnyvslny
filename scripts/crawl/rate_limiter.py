"""Per-domain token bucket rate limiter."""

import time
from urllib.parse import urlparse


class RateLimiter:
    """Enforces a minimum delay between requests to the same domain."""

    def __init__(self, default_delay: float = 1.0):
        self._default_delay = default_delay
        self._last_request: dict[str, float] = {}

    def wait(self, url: str) -> None:
        """Block until it's safe to request the given URL's domain."""
        domain = urlparse(url).netloc
        now = time.monotonic()
        last = self._last_request.get(domain, 0.0)
        wait_time = self._default_delay - (now - last)
        if wait_time > 0:
            time.sleep(wait_time)
        self._last_request[domain] = time.monotonic()
