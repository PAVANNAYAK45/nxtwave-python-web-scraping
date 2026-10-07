"""Small HTTP client with retries, timeouts, rate limiting and logging."""

from __future__ import annotations

import logging
import time
from typing import Optional

import requests
from requests import Response


class HttpClient:
    def __init__(
        self,
        *,
        timeout: float = 15.0,
        max_retries: int = 3,
        backoff: float = 1.0,
        delay: float = 0.2,
        user_agent: str = "NxtWave-WebScraping-Assignment/1.0",
    ) -> None:
        self.timeout = timeout
        self.max_retries = max(0, max_retries)
        self.backoff = max(0.0, backoff)
        self.delay = max(0.0, delay)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.logger = logging.getLogger(__name__)
        self._last_request_at = 0.0

    def get(self, url: str) -> Optional[Response]:
        """GET a URL, retrying transient failures and returning None on failure."""
        for attempt in range(self.max_retries + 1):
            self._respect_rate_limit()
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                self.logger.debug("GET %s -> %s", url, response.status_code)
                return response
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    self.logger.error("Request failed after %s attempts: %s | %s", attempt + 1, url, exc)
                    return None
                sleep_for = self.backoff * (2 ** attempt)
                self.logger.warning(
                    "Request failed (attempt %s/%s): %s | retrying in %.1fs | %s",
                    attempt + 1,
                    self.max_retries + 1,
                    exc,
                    sleep_for,
                    url,
                )
                time.sleep(sleep_for)
        return None

    def _respect_rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        remaining = self.delay - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._last_request_at = time.monotonic()
