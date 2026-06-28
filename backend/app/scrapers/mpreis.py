import asyncio
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright

from app.scrapers.base import Category, RawProductPayload


class MpreisScraper:
    retailer = "mpreis"
    country = "AT"
    base_url = "https://www.mpreis.at"
    category_url = "https://www.mpreis.at/schneller-erster-einkauf"

    def __init__(self, *, max_products_per_category: int = 3) -> None:
        self.max_products_per_category = min(max_products_per_category, 3)

    async def scrape_categories(self) -> list[Category]:
        return [
            Category(
                name="Schneller erster Einkauf",
                url=self.category_url,
                source_id="schneller-erster-einkauf",
                parent_name="MPREIS Sortiment",
            )
        ]

    async def scrape_products(self, category: Category) -> list[RawProductPayload]:
        html = await self._fetch_html(category.url)
        products = self._parse_products(html, category=category)
        return products[: self.max_products_per_category]

    async def _fetch_html(self, url: str) -> str:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(2)
            html = await page.content()
            await browser.close()
            return html

    def _parse_products(self, html: str, *, category: Category) -> list[RawProductPayload]:
        soup = BeautifulSoup(html, "lxml")
        products: list[RawProductPayload] = []
        seen_ids: set[str] = set()

        for card in soup.select("a.c3-product[href]"):
            product_url = urljoin(self.base_url, str(card.get("href")))
            if not _is_mpreis_url(product_url):
                continue

            source_product_id = _source_id_from_card(card, product_url)
            if not source_product_id or source_product_id in seen_ids:
                continue

            brand = _select_text(card, ".c3-product__producer")
            product_name = _select_text(card, ".c3-product__name")
            name = " ".join(value for value in [brand, product_name] if value)
            if not name:
                continue

            seen_ids.add(source_product_id)
            card_text = _clean_text(card.get_text(" ", strip=True))
            products.append(
                RawProductPayload(
                    retailer=self.retailer,
                    country=self.country,
                    source_url=product_url,
                    source_product_id=source_product_id,
                    name=name,
                    brand=brand,
                    category=category.name,
                    price=_extract_price(card),
                    unit_price=_select_text(card, ".c3-product__unit"),
                    package_size=_select_text(card, ".c3-product__weight-info-text"),
                    currency="EUR",
                    availability=_extract_availability(card_text),
                    promotion_text=_extract_promotion_text(card_text),
                    raw_payload={
                        "category_url": category.url,
                        "card_text": card_text,
                        "location_context": "no_market_selected",
                    },
                )
            )

        return products


def _source_id_from_card(card: Tag, product_url: str) -> str | None:
    for class_name in card.get("class", []):
        match = re.fullmatch(r"c3-item-(\d+)", str(class_name))
        if match:
            return match.group(1)

    path = urlparse(product_url).path.rstrip("/")
    match = re.search(r"-(\d+)$", path)
    return match.group(1) if match else None


def _extract_price(card: Tag) -> str | None:
    value = _select_text(card, ".c3-product__price-value")
    if not value:
        return None
    return f"{value} €" if "€" not in value else value


def _extract_availability(text: str) -> str | None:
    markers = [
        "Verfügbarkeit in deinem Markt prüfen",
        "Noch kein Markt gewählt",
        "Verfügbarkeit in allen Märkten prüfen",
    ]
    found = [marker for marker in markers if marker in text]
    return "; ".join(found) if found else None


def _extract_promotion_text(text: str) -> str | None:
    markers = [
        "NUR MIT APP",
        "ab 2 billiger",
        "ab 3 billiger",
        "1+1 gratis",
        "2+2 gratis",
        "-25%",
        "-33%",
        "-50%",
    ]
    found = [marker for marker in markers if marker in text]
    return "; ".join(found) if found else None


def _select_text(card: Tag, selector: str) -> str | None:
    element = card.select_one(selector)
    if element is None:
        return None
    value = _clean_text(element.get_text(" ", strip=True))
    return value or None


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _is_mpreis_url(url: str) -> bool:
    return urlparse(url).netloc.endswith("mpreis.at")
