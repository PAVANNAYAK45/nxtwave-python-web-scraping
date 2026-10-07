"""Deterministic duplicate detection."""

from __future__ import annotations

from .cleaning import normalize_key


def duplicate_key(record: dict) -> tuple:
    """Use normalized source, title/content, author and URL.

    Including source prevents unrelated records from different sites with the same
    title from being accidentally discarded. The normalized title/author catches
    whitespace/case/formatting differences within a source.
    """
    return (
        normalize_key(record.get("source")),
        normalize_key(record.get("name_or_title")),
        normalize_key(record.get("author")),
        normalize_key(record.get("source_url")),
    )


def deduplicate(records: list[dict]) -> tuple[list[dict], int]:
    seen: set[tuple] = set()
    unique: list[dict] = []
    duplicate_count = 0
    for record in records:
        key = duplicate_key(record)
        if key in seen:
            duplicate_count += 1
            continue
        seen.add(key)
        unique.append(record)
    return unique, duplicate_count
