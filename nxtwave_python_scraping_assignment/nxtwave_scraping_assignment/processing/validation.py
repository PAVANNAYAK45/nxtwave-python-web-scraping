"""Record validation."""

from __future__ import annotations

from .cleaning import is_valid_url


def validate_record(record: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not record.get("source"):
        errors.append("missing_source")
    if not record.get("source_url") or not is_valid_url(record.get("source_url")):
        errors.append("invalid_source_url")
    if not record.get("name_or_title"):
        errors.append("missing_name_or_title")

    price = record.get("price")
    if price is not None:
        try:
            if float(price) < 0:
                errors.append("negative_price")
        except (TypeError, ValueError):
            errors.append("non_numeric_price")

    rating = record.get("rating")
    if rating is not None:
        try:
            if not 1 <= int(rating) <= 5:
                errors.append("rating_out_of_range")
        except (TypeError, ValueError):
            errors.append("invalid_rating")

    return not errors, errors
