from processing.cleaning import clean_record, normalize_key, parse_price
from processing.deduplication import deduplicate
from processing.validation import validate_record


def test_clean_text_and_price():
    record = clean_record({
        "source": " Books  to   Scrape ",
        "source_url": "https://books.toscrape.com/catalogue/a_1/index.html",
        "name_or_title": "  Example   Book  ",
        "price": "£51.77",
        "rating": "5",
    })
    assert record["source"] == "Books to Scrape"
    assert record["name_or_title"] == "Example Book"
    assert record["price"] == 51.77
    assert record["rating"] == 5


def test_normalized_key_ignores_case_and_punctuation():
    assert normalize_key(" Example Book Title! ") == normalize_key("EXAMPLE   BOOK TITLE")


def test_validation():
    valid = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/a",
        "name_or_title": "Book",
        "price": 10.0,
        "rating": 4,
    }
    assert validate_record(valid)[0] is True
    invalid = dict(valid, rating=9)
    assert validate_record(invalid)[0] is False


def test_deduplication():
    base = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalogue/a/index.html",
        "name_or_title": " Example Book ",
        "author": "",
    }
    duplicate = dict(base, name_or_title="EXAMPLE BOOK")
    unique, count = deduplicate([base, duplicate])
    assert len(unique) == 1
    assert count == 1
