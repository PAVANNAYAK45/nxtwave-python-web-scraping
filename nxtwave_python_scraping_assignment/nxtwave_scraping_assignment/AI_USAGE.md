# AI_USAGE.md

## AI tools used

- ChatGPT

## What AI was used for

ChatGPT was used as an engineering assistant for:

- breaking the assignment into modules;
- proposing a clean project structure;
- drafting initial Requests + BeautifulSoup scraper code;
- designing the common record schema;
- suggesting cleaning and validation functions;
- reviewing duplicate-detection logic;
- designing retry/backoff and logging behavior;
- generating unit-test cases;
- improving README documentation;
- preparing likely interview follow-up questions.

## Representative prompts

1. "Design a medium-level Python web scraping project that follows the supplied assignment requirements for Books to Scrape and Quotes to Scrape."
2. "Create separate Requests + BeautifulSoup scrapers with dynamic next-page pagination and source-specific parsing."
3. "Review this duplicate detection strategy and make it robust to whitespace and capitalization differences without inventing data."
4. "Generate unit tests for cleaning, validation, duplicate detection, and representative HTML parsing."

## AI-assisted parts

The following areas were AI-assisted during initial implementation:

- module scaffolding;
- HTTP client structure;
- scraper parsing patterns;
- processing functions;
- tests;
- documentation.

## Human review and changes

The generated implementation was reviewed against the assignment requirements. The final design deliberately keeps scraping separate from processing, uses configurable delays/retries, follows actual next-page links, validates records before writing output, and keeps source URLs. The duplicate key includes the source to avoid incorrectly removing similarly named records from different websites.

## Incorrect/incomplete suggestions discovered

No AI-generated output is treated as authoritative. Selectors, pagination behavior, and output fields should be verified by running the scraper against the supplied websites. If a selector changes, it should be updated in the relevant source-specific scraper rather than silently inventing data.

## Verification

The final solution was tested locally using Python 3.14.7.

Test execution:

```bash
python -m pytest
```

After execution, inspect:

- `output/final_dataset.csv` for standardized records;
- `output/summary_report.json` for counts and validation/deduplication metrics;
- `logs/scraper.log` for page-level activity and failures.

Representative records should also be manually checked against the public source pages.
