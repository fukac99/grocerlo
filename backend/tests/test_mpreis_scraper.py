from app.scrapers.base import Category
from app.scrapers.mpreis import MpreisScraper


def test_mpreis_parser_extracts_public_product_fields() -> None:
    scraper = MpreisScraper(max_products_per_category=3)
    category = Category(
        name="Schneller erster Einkauf",
        url="https://www.mpreis.at/schneller-erster-einkauf",
        source_id="schneller-erster-einkauf",
    )

    products = scraper._parse_products(
        """
        <a href="/shop/p/bio-vom-berg-bio-eier-ml-6er-packung-500167"
           class="c3-product c3-item-500167">
          <span class="c3-product__producer">BIO vom BERG</span>
          <span class="c3-product__name">Bio Eier M/L 6er-Packung</span>
          <div class="c3-product__weight-info-text">6STK</div>
          <span class="c3-product__price-value">3,59</span>
          <div class="c3-product__unit">0,60 € /Stk</div>
          <div class="c3-product__price-discount-app">NUR MIT APP</div>
          <div>Verfügbarkeit in deinem Markt prüfen</div>
          <div>Noch kein Markt gewählt</div>
          <p>Verfügbarkeit in allen Märkten prüfen</p>
        </a>
        """,
        category=category,
    )

    assert len(products) == 1
    assert products[0].retailer == "mpreis"
    assert products[0].country == "AT"
    assert products[0].source_product_id == "500167"
    assert (
        products[0].source_url
        == "https://www.mpreis.at/shop/p/bio-vom-berg-bio-eier-ml-6er-packung-500167"
    )
    assert products[0].name == "BIO vom BERG Bio Eier M/L 6er-Packung"
    assert products[0].brand == "BIO vom BERG"
    assert products[0].price == "3,59 €"
    assert products[0].unit_price == "0,60 € /Stk"
    assert products[0].package_size == "6STK"
    assert products[0].promotion_text == "NUR MIT APP"
    assert products[0].availability == (
        "Verfügbarkeit in deinem Markt prüfen; Noch kein Markt gewählt; "
        "Verfügbarkeit in allen Märkten prüfen"
    )
    assert products[0].raw_payload["location_context"] == "no_market_selected"


def test_mpreis_scraper_caps_discovery_volume_to_three_products() -> None:
    scraper = MpreisScraper(max_products_per_category=20)

    assert scraper.max_products_per_category == 3
