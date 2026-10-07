"""Main entry point for the NxtWave Python web scraping assignment."""

from __future__ import annotations

import argparse
import json
import logging
import time
from collections import Counter
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import deduplicate
from processing.output import write_csv, write_json
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.http_client import HttpClient
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).resolve().parent


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def configure_logging(log_file: Path, level: str = "INFO") -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
        force=True,
    )


def run(config: dict, output_dir: Path, log_file: Path) -> dict:
    configure_logging(log_file)
    logger = logging.getLogger("main")
    started = time.perf_counter()
    started_at_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    client = HttpClient(
        timeout=config.get("request_timeout_seconds", 15),
        max_retries=config.get("max_retries", 3),
        backoff=config.get("retry_backoff_seconds", 1.0),
        delay=config.get("delay_between_requests_seconds", 0.2),
        user_agent=config.get("user_agent", "NxtWave-WebScraping-Assignment/1.0"),
    )

    raw_records: list[dict] = []
    source_collected = Counter()

    logger.info("Starting Books to Scrape")
    for record in BooksScraper(client, fetch_details=config.get("fetch_book_details", True)).scrape():
        raw_records.append(record)
        source_collected[record.get("source", "unknown")] += 1

    logger.info("Starting Quotes to Scrape")
    for record in QuotesScraper(client, fetch_author_details=config.get("fetch_quote_author_details", True)).scrape():
        raw_records.append(record)
        source_collected[record.get("source", "unknown")] += 1

    cleaned_records = [clean_record(record) for record in raw_records]

    valid_records: list[dict] = []
    rejected_records = []
    validation_error_counts = Counter()
    for record in cleaned_records:
        valid, errors = validate_record(record)
        if valid:
            valid_records.append(record)
        else:
            record["validation_errors"] = ";".join(errors)
            rejected_records.append(record)
            validation_error_counts.update(errors)

    unique_records, duplicate_count = deduplicate(valid_records)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(unique_records, output_dir / "final_dataset.csv")

    duration = time.perf_counter() - started
    cleaned_counts = Counter(r.get("source", "unknown") for r in cleaned_records)
    final_counts = Counter(r.get("source", "unknown") for r in unique_records)
    rejected_counts = Counter(r.get("source", "unknown") for r in rejected_records)

    summary = {
        "assignment": "NxtWave Python Web Scraping Interview Assignment",
        "execution": {
            "duration_seconds": round(duration, 3),
            "started_at_utc": started_at_utc,
        },
        "records": {
            "total_collected": len(raw_records),
            "collected_per_source": dict(source_collected),
            "total_after_cleaning": len(cleaned_records),
            "after_cleaning_per_source": dict(cleaned_counts),
            "rejected_during_validation": len(rejected_records),
            "rejected_per_source": dict(rejected_counts),
            "validation_errors": dict(validation_error_counts),
            "duplicates_detected_and_removed": duplicate_count,
            "final_record_count": len(unique_records),
            "final_per_source": dict(final_counts),
        },
        "configuration": {
            "fetch_book_details": bool(config.get("fetch_book_details", True)),
            "fetch_quote_author_details": bool(config.get("fetch_quote_author_details", True)),
            "delay_between_requests_seconds": config.get("delay_between_requests_seconds", 0.2),
            "max_retries": config.get("max_retries", 3),
        },
        "outputs": ["final_dataset.csv", "summary_report.json"],
    }
    write_json(summary, output_dir / "summary_report.json")
    logger.info("Finished. collected=%s valid=%s rejected=%s duplicates=%s final=%s", len(raw_records), len(valid_records), len(rejected_records), duplicate_count, len(unique_records))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape and consolidate Books to Scrape + Quotes to Scrape")
    parser.add_argument("--config", type=Path, default=ROOT / "config.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    parser.add_argument("--log-file", type=Path, default=ROOT / "logs" / "scraper.log")
    args = parser.parse_args()
    config = load_config(args.config)
    run(config, args.output_dir, args.log_file)


if __name__ == "__main__":
    main()
