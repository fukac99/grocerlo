from app.scrapers.base import Category
from app.scrapers.base import ScraperStopCondition
from app.scrapers.rewe import APPROVED_REWE_LOCATION_CONTEXT, ReweScraper


def test_rewe_parser_extracts_location_scoped_product_fields() -> None:
    scraper = ReweScraper(max_products_per_category=3)
    category = Category(
        name="Approved Idstein-Wörsdorf product sample",
        url="https://www.rewe.de/shop/",
        source_id="idstein-woersdorf-sample",
    )

    product = scraper._parse_product_page(
        """
        <html>
          <head><title>REWE Bio Frische Vollmilch 3,8% 1l | REWE online bestellen</title></head>
          <body>
            <h1>REWE Bio Frische Vollmilch 3,8% 1l</h1>
            <span>Tiefpreis</span>
            <span>1,59 €</span>
            <span>1,59 € / l</span>
            <span>Online verfügbar</span>
          </body>
        </html>
        """,
        url="https://www.rewe.de/shop/p/rewe-bio-frische-vollmilch-3-8-1l/8846520?ecid=test",
        category=category,
    )

    assert product is not None
    assert product.retailer == "rewe"
    assert product.country == "DE"
    assert product.source_product_id == "8846520"
    assert product.source_url == "https://www.rewe.de/shop/p/rewe-bio-frische-vollmilch-3-8-1l/8846520"
    assert product.name == "REWE Bio Frische Vollmilch 3,8% 1l"
    assert product.brand == "REWE Bio"
    assert product.price == "1,59 €"
    assert product.unit_price == "1,59 € / l"
    assert product.package_size == "1l"
    assert product.currency == "EUR"
    assert product.availability == "Online verfügbar"
    assert product.promotion_text == "Tiefpreis"
    assert product.raw_payload["location_context"] == APPROVED_REWE_LOCATION_CONTEXT
    assert product.raw_payload["location_selection_attempted"] is False


def test_rewe_parser_preserves_no_location_price_placeholder() -> None:
    scraper = ReweScraper()
    category = Category(
        name="Approved Idstein-Wörsdorf product sample",
        url="https://www.rewe.de/shop/",
        source_id="idstein-woersdorf-sample",
    )

    product = scraper._parse_product_page(
        """
        <h1>ja! Banane ca. 200g</h1>
        <span>Konkreter Preis abhängig vom Standort</span>
        <button>Standort wählen</button>
        """,
        url="https://www.rewe.de/shop/p/ja-banane-ca-200g/455217",
        category=category,
    )

    assert product is not None
    assert product.price is None
    assert product.currency is None
    assert product.package_size == "ca. 200g"
    assert product.availability == "Konkreter Preis abhängig vom Standort; Standort wählen"
    assert product.raw_payload["price_placeholder"] == "Konkreter Preis abhängig vom Standort"


def test_rewe_scraper_caps_dry_run_volume_to_three_products() -> None:
    scraper = ReweScraper(max_products_per_category=50)

    assert scraper.max_products_per_category == 3


def test_rewe_parser_stops_on_bot_protection_challenge() -> None:
    scraper = ReweScraper()
    category = Category(
        name="Approved Idstein-Wörsdorf product sample",
        url="https://www.rewe.de/shop/",
        source_id="idstein-woersdorf-sample",
    )

    try:
        scraper._parse_product_page(
            """
            <title>Just a moment...</title>
            <h1>Zeig uns, dass du ein Mensch bist.</h1>
            <p>WAF Challenge Bot protection</p>
            """,
            url="https://www.rewe.de/shop/p/rewe-bio-frische-vollmilch-3-8-1l/8846520",
            category=category,
        )
    except ScraperStopCondition as exc:
        assert str(exc) == "REWE stop condition: bot protection challenge"
    else:
        raise AssertionError("Expected bot protection to stop the REWE dry run")
