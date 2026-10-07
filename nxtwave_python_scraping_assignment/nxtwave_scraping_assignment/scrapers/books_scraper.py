"""Scraper for https://books.toscrape.com/."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, Iterator, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .http_client import HttpClient

BASE_URL = "https://books.toscrape.com/"


class BooksScraper:
    def __init__(self, client: HttpClient, fetch_details: bool = True) -> None:
        self.client = client
        self.fetch_details = fetch_details
        self.logger = logging.getLogger(__name__)

    def scrape(self) -> Iterator[dict]:
        url = BASE_URL
        page_number = 0
        while url:
            page_number += 1
            response = self.client.get(url)
            if response is None:
                self.logger.error("Skipping books page %s because it could not be fetched: %s", page_number, url)
                # A page failure should not crash the entire pipeline. We cannot safely infer the next page.
                break

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.select("article.product_pod")
            self.logger.info("Books page %s: found %s records", page_number, len(cards))

            for card in cards:
                try:
                    record = self.parse_card(card, url)
                    if self.fetch_details and record.get("source_url"):
                        detail = self._fetch_detail(record["source_url"])
                        record.update(detail)
                    yield record
                except Exception as exc:  # defensive: one malformed card must not stop the page
                    self.logger.exception("Failed to parse a book card on %s: %s", url, exc)

            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link.get("href")) if next_link and next_link.get("href") else ""

    def parse_card(self, card, page_url: str) -> dict:
        title_node = card.select_one("h3 a")
        price_node = card.select_one(".price_color")
        availability_node = card.select_one(".availability")
        rating_node = card.select_one("p.star-rating")
        image_node = card.select_one("div.image_container img")

        title = title_node.get("title", "") if title_node else ""
        product_url = urljoin(page_url, title_node.get("href", "")) if title_node else ""
        price_text = price_node.get_text(" ", strip=True) if price_node else ""
        availability = availability_node.get_text(" ", strip=True) if availability_node else ""
        rating = self._rating_from_classes(rating_node.get("class", [])) if rating_node else None
        image_url = urljoin(page_url, image_node.get("src", "")) if image_node else ""

        return {
            "source": "Books to Scrape",
            "source_url": product_url,
            "name_or_title": title,
            "category": "",
            "price": price_text,
            "rating": rating,
            "author": "",
            "tags": "",
            "description": "",
            "availability": availability,
            "image_url": image_url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    def _fetch_detail(self, url: str) -> dict:
        response = self.client.get(url)
        if response is None:
            return {}
        soup = BeautifulSoup(response.text, "html.parser")
        category_node = soup.select_one("ul.breadcrumb li:nth-of-type(3) a")
        description_node = soup.select_one("#product_description + p")
        return {
            "category": category_node.get_text(" ", strip=True) if category_node else "",
            "description": description_node.get_text(" ", strip=True) if description_node else "",
        }

    @staticmethod
    def _rating_from_classes(classes: list[str]) -> Optional[int]:
        mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        for name, value in mapping.items():
            if name in classes:
                return value
        return None
