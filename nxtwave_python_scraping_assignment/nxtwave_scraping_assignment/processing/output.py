"""CSV and JSON output helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path

DATASET_FIELDS = [
    "source", "source_url", "name_or_title", "category", "price", "rating",
    "author", "tags", "description", "availability", "image_url",
    "author_url", "author_birth_date", "author_birth_location", "scraped_at",
]


def write_csv(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=DATASET_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field, "") for field in DATASET_FIELDS})


def write_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
