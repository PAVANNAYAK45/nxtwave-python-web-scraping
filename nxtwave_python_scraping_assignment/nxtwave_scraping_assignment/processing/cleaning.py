"""Cleaning and standardization functions."""

from __future__ import annotations

import re
from urllib.parse import urlparse


def clean_text(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_key(value) -> str:
    text = clean_text(value).casefold()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def parse_price(value):
    if value is None or value == "":
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group()) if match else None


def normalize_rating(value):
    if value in (None, ""):
        return None
    try:
        rating = int(float(value))
    except (TypeError, ValueError):
        return None
    return rating if 1 <= rating <= 5 else None


def clean_record(record: dict) -> dict:
    cleaned = dict(record)
    text_fields = [
        "source", "source_url", "name_or_title", "category", "author", "tags",
        "description", "availability", "image_url", "author_url",
        "author_birth_date", "author_birth_location",
    ]
    for field in text_fields:
        cleaned[field] = clean_text(cleaned.get(field))
    cleaned["price"] = parse_price(cleaned.get("price"))
    cleaned["rating"] = normalize_rating(cleaned.get("rating"))
    return cleaned


def is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value or "")
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False
