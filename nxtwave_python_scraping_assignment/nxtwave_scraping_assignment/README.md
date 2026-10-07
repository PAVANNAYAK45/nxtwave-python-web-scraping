# NxtWave Python Web Scraping Interview Assignment

## 1. Overview

This project implements a reusable Python web-scraping and data-consolidation pipeline for the two public practice websites specified in the assignment:

- Books to Scrape: https://books.toscrape.com/
- Quotes to Scrape: https://quotes.toscrape.com/

The pipeline performs scraping, pagination, cleaning, validation, duplicate detection, consolidation, logging, and output generation.

## 2. Python version

Python 3.10+ is recommended. The project was written using standard Python typing and tested with Python 3.11+.

## 3. Project structure

```text
nxtwave_scraping_assignment/
├── scrapers/
│   ├── __init__.py
│   ├── http_client.py
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── __init__.py
│   ├── cleaning.py
│   ├── validation.py
│   ├── deduplication.py
│   └── output.py
├── output/
│   ├── final_dataset.csv
│   └── summary_report.json
├── logs/
│   └── scraper.log
├── tests/
│   ├── test_processing.py
│   └── test_scrapers.py
├── config.json
├── main.py
├── requirements.txt
├── README.md
├── AI_USAGE.md
└── .gitignore
```

## 4. Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 5. Run the scraper

From the project root:

```bash
python main.py
```

Optional custom paths:

```bash
python main.py --config config.json --output-dir output --log-file logs/scraper.log
```

The run produces:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

## 6. Scraping approach

### Books to Scrape

`BooksScraper` starts at the home page, extracts book cards, and follows the site's `li.next > a` link until there is no next page. Each book captures title, product URL, price, availability, rating, and image URL. When `fetch_book_details` is enabled, the scraper additionally requests each product page to obtain category and description.

### Quotes to Scrape

`QuotesScraper` starts at the home page, extracts quote cards, and follows the `li.next > a` link until pagination ends. It captures quote text, author, tags, page URL, and author URL. When `fetch_quote_author_details` is enabled, author pages are requested and cached to collect birth date, birth location, and author description.

Pagination is selector-driven; page numbers are not hard-coded.

## 7. Standardized data model

The final CSV uses these fields:

- `source`
- `source_url`
- `name_or_title`
- `category`
- `price`
- `rating`
- `author`
- `tags`
- `description`
- `availability`
- `image_url`
- `author_url`
- `author_birth_date`
- `author_birth_location`
- `scraped_at`

Fields that do not apply to a source are represented by empty values/NULL-like CSV values rather than invented data.

## 8. Cleaning

Cleaning is deliberately separated from scraping. `processing/cleaning.py`:

- removes repeated/leading/trailing whitespace;
- normalizes text to a single-space representation;
- converts book prices to numeric floats;
- converts ratings to integer values;
- preserves missing values as empty/None;
- provides a normalized key for duplicate detection.

## 9. Validation

Before consolidation, each record is checked for:

- recognizable source;
- valid HTTP/HTTPS source URL;
- non-empty title/quote;
- numeric, non-negative price when present;
- rating between 1 and 5 when present.

Invalid records are rejected and counted in the summary instead of crashing the complete run.

## 10. Duplicate detection

Duplicate detection uses a normalized tuple of:

1. source;
2. name/title or quote text;
3. author;
4. source URL.

Whitespace, capitalization, and punctuation differences are normalized before comparison. The source is included intentionally so that unrelated records on different sites with the same title are not accidentally removed.

The first occurrence is retained and later equivalent records are removed. The number removed is reported in `summary_report.json`.

## 11. Error handling and logging

`HttpClient` provides:

- request timeouts;
- HTTP error handling;
- retries;
- exponential backoff;
- configurable delay between requests;
- a descriptive user agent.

A failed page is logged and does not raise an uncaught exception that stops the whole program. Individual malformed cards are also isolated with exception handling.

## 12. Configuration

Edit `config.json` to control:

- timeout;
- retry count;
- retry backoff;
- delay between requests;
- whether product detail pages are fetched;
- whether quote author pages are fetched;
- user agent.

For a faster demo run, set both detail flags to `false`. For the complete assignment output, leave them `true`.

## 13. Tests

Run:

```bash
pytest -q
```

Tests cover cleaning, numeric conversion, validation, duplicate detection, and representative HTML parsing for both sources.

## 14. Output summary

`summary_report.json` records:

- total records collected per source;
- total after cleaning;
- rejected records;
- validation error counts;
- duplicates detected and removed;
- final record count;
- final counts by source;
- execution duration;
- relevant configuration.

## 15. Assumptions

- The two supplied websites remain available using their public HTML pages.
- Their pagination can be discovered through the site's next-page link.
- Source-specific HTML selectors may change in the future; selectors are isolated inside each scraper so they can be updated independently.
- Empty fields are preferable to fabricated data.
- A reasonable request delay is used to avoid unnecessarily aggressive traffic.

## 16. Known limitations

- This is an interview assignment, not a distributed production crawler.
- It uses synchronous requests.
- If a website changes its HTML structure, selectors may require maintenance.
- A failure on a page cannot always be followed to the next page because the next-page URL is learned from the failed page.
- Detail-page fetching increases request count and therefore execution time.

## 17. Ethical/safety constraints

Only the publicly accessible pages specified by the assignment are used. The scraper does not bypass authentication, CAPTCHAs, access controls, or security mechanisms, and it does not contain credentials or API keys.

## 18. Interview explanation in one minute

I chose Requests with BeautifulSoup because both sources expose straightforward server-rendered HTML, so a browser automation tool is unnecessary. Each source has its own scraper to keep selectors isolated. Pagination follows the site's next link rather than hard-coding page numbers. After scraping, a separate processing layer cleans text, converts prices and ratings, validates required fields, and removes normalized duplicates. A shared HTTP client handles timeouts, retries, exponential backoff, rate limiting, and logging. Finally, the pipeline writes a standardized CSV and a JSON summary so the reviewer can see what was collected, rejected, deduplicated, and retained.
