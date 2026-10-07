from bs4 import BeautifulSoup

from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper


class DummyClient:
    pass


def test_books_card_parser():
    html = '''
    <article class="product_pod">
      <p class="star-rating Three"></p>
      <h3><a href="catalogue/example_1/index.html" title=" Example Book ">Example</a></h3>
      <div class="product_price"><p class="price_color">£10.50</p><p class="availability"> In stock </p></div>
    </article>
    '''
    card = BeautifulSoup(html, "html.parser").select_one("article")
    record = BooksScraper(DummyClient(), fetch_details=False).parse_card(card, "https://books.toscrape.com/")
    assert record["name_or_title"] == " Example Book "
    assert record["rating"] == 3
    assert record["source_url"].endswith("catalogue/example_1/index.html")


def test_quotes_card_parser():
    html = '''
    <div class="quote">
      <span class="text">“A test quote.”</span>
      <small class="author">Test Author</small>
      <span><a href="/author/test-author">about</a></span>
      <div class="tags"><a class="tag">test</a><a class="tag">python</a></div>
    </div>
    '''
    card = BeautifulSoup(html, "html.parser").select_one("div.quote")
    record = QuotesScraper(DummyClient(), fetch_author_details=False).parse_card(card, "https://quotes.toscrape.com/")
    assert record["name_or_title"] == "“A test quote.”"
    assert record["author"] == "Test Author"
    assert record["tags"] == "test, python"
    assert record["author_url"].endswith("/author/test-author")
