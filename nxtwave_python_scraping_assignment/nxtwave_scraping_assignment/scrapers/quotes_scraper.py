"""Scraper for https://quotes.toscrape.com/."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .http_client import HttpClient

BASE_URL = "https://quotes.toscrape.com/"


class QuotesScraper:
    def __init__(self, client: HttpClient, fetch_author_details: bool = True) -> None:
        self.client = client
        self.fetch_author_details = fetch_author_details
        self.logger = logging.getLogger(__name__)
        self._author_cache: dict[str, dict] = {}

    def scrape(self):
        url = BASE_URL
        page_number = 0
        while url:
            page_number += 1
            response = self.client.get(url)
            if response is None:
                self.logger.error("Skipping quotes page %s because it could not be fetched: %s", page_number, url)
                break

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.select("div.quote")
            self.logger.info("Quotes page %s: found %s records", page_number, len(cards))

            for card in cards:
                try:
                    record = self.parse_card(card, url)
                    if self.fetch_author_details and record.get("author_url"):
                        record.update(self._fetch_author(record["author_url"]))
                    yield record
                except Exception as exc:
                    self.logger.exception("Failed to parse quote card on %s: %s", url, exc)

            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link.get("href")) if next_link and next_link.get("href") else ""

    def parse_card(self, card, page_url: str) -> dict:
        text_node = card.select_one("span.text")
        author_node = card.select_one("small.author")
        author_link = card.select_one("span a")
        tag_nodes = card.select("div.tags a.tag")

        author_url = urljoin(page_url, author_link.get("href", "")) if author_link else ""
        quote = text_node.get_text(" ", strip=True) if text_node else ""
        author = author_node.get_text(" ", strip=True) if author_node else ""
        tags = ", ".join(tag.get_text(" ", strip=True) for tag in tag_nodes)

        return {
            "source": "Quotes to Scrape",
            "source_url": page_url,
            "name_or_title": quote,
            "category": "",
            "price": None,
            "rating": None,
            "author": author,
            "tags": tags,
            "description": "",
            "availability": "",
            "image_url": "",
            "author_url": author_url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    def _fetch_author(self, url: str) -> dict:
        if url in self._author_cache:
            return self._author_cache[url]
        response = self.client.get(url)
        if response is None:
            return {}
        soup = BeautifulSoup(response.text, "html.parser")
        born_date = soup.select_one("span.author-born-date")
        born_location = soup.select_one("span.author-born-location")
        bio = soup.select_one("div.author-description")
        result = {
            "author_birth_date": born_date.get_text(" ", strip=True) if born_date else "",
            "author_birth_location": born_location.get_text(" ", strip=True) if born_location else "",
            "description": bio.get_text(" ", strip=True) if bio else "",
        }
        self._author_cache[url] = result
        return result
