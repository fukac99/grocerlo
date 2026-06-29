import asyncio
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.scrapers.base import Category, RawProductPayload, ScraperStopCondition


APPROVED_REWE_LOCATION_CONTEXT = "65510 Idstein-Wörsdorf"
REWE_SAMPLE_PRODUCT_URLS = [
    "https://www.rewe.de/shop/p/rewe-bio-frische-vollmilch-3-8-1l/8846520",
    "https://www.rewe.de/shop/p/rewe-beste-wahl-spaghetti-n-3-500g/2632428",
    "https://www.rewe.de/shop/p/ja-banane-ca-200g/455217",
]


class ReweScraper:
    retailer = "rewe"
    country = "DE"
    base_url = "https://www.rewe.de"
    category_url = "https://www.rewe.de/shop/"

    def __init__(
        self,
        *,
        max_products_per_category: int = 3,
        location_context: str = APPROVED_REWE_LOCATION_CONTEXT,
    ) -> None:
        self.max_products_per_category = max(1, min(max_products_per_category, 3))
        self.location_context = location_context

    async def scrape_categories(self) -> list[Category]:
        return [
            Category(
                name="Approved Idstein-Wörsdorf product sample",
                url=self.category_url,
                source_id="idstein-woersdorf-sample",
                parent_name="REWE Shop",
            )
        ]

    async def scrape_products(self, category: Category) -> list[RawProductPayload]:
        products: list[RawProductPayload] = []
        for product_url in REWE_SAMPLE_PRODUCT_URLS[: self.max_products_per_category]:
            html = await self._fetch_html(product_url)
            product = self._parse_product_page(html, url=product_url, category=category)
            if product is not None:
                products.append(product)
        return products

    async def _fetch_html(self, url: str) -> str:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
            html = await page.content()
            await browser.close()
            return html

    def _parse_product_page(
        self,
        html: str,
        *,
        url: str,
        category: Category,
    ) -> RawProductPayload | None:
        if not _is_rewe_url(url):
            return None

        soup = BeautifulSoup(html, "lxml")
        page_text = _clean_text(soup.get_text(" ", strip=True))
        stop_condition = _detect_stop_condition(page_text)
        if stop_condition:
            raise ScraperStopCondition(f"REWE stop condition: {stop_condition}")

        name = _extract_name(soup)
        source_product_id = _source_id_from_url(url)
        if not name or not source_product_id:
            return None

        price = _extract_price(page_text)
        return RawProductPayload(
            retailer=self.retailer,
            country=self.country,
            source_url=_canonical_product_url(url),
            source_product_id=source_product_id,
            name=name,
            brand=_guess_brand(name),
            category=category.name,
            price=price,
            unit_price=_extract_unit_price(page_text),
            package_size=_extract_package_size(name, page_text),
            currency="EUR" if price else None,
            availability=_extract_availability(page_text),
            promotion_text=_extract_promotion_text(page_text),
            raw_payload={
                "category_url": category.url,
                "location_context": self.location_context,
                "location_selection_attempted": False,
                "price_placeholder": _extract_price_placeholder(page_text),
                "card_text": page_text[:2000],
            },
        )


def _extract_name(soup: BeautifulSoup) -> str | None:
    for selector in ["h1", "[data-testid='pdp-product-title']"]:
        element = soup.select_one(selector)
        if element is None:
            continue
        value = _clean_text(element.get_text(" ", strip=True))
        if value:
            return value

    title = soup.find("title")
    if title is None:
        return None
    value = _clean_text(title.get_text(" ", strip=True))
    return value.removesuffix("| REWE online bestellen").strip() or None


def _extract_price(text: str) -> str | None:
    if _extract_price_placeholder(text):
        return None

    match = re.search(r"(?<!\d)(\d+,\d{2})\s*€", text)
    return f"{match.group(1)} €" if match else None


def _extract_unit_price(text: str) -> str | None:
    match = re.search(r"\d+,\d{2}\s*€\s*/\s*(?:kg|g|l|ml|Stk|Stück)", text, re.IGNORECASE)
    return match.group(0) if match else None


def _extract_package_size(name: str, text: str) -> str | None:
    for value in [name, text]:
        match = re.search(
            r"(?:ca\.\s*)?\d+(?:,\d+)?\s*(?:kg|g|l|ml|liter|Liter|Stk|Stück)",
            value,
        )
        if match:
            return match.group(0)
    return None


def _extract_availability(text: str) -> str | None:
    markers = [
        "Konkreter Preis abhängig vom Standort",
        "Standort wählen",
        "Aktuell nicht verfügbar",
        "Online verfügbar",
    ]
    found = [marker for marker in markers if marker in text]
    return "; ".join(found) if found else None


def _extract_promotion_text(text: str) -> str | None:
    markers = ["Tiefpreis", "REWE Bonus", "PAYBACK", "Aktion", "Angebot"]
    found = [marker for marker in markers if marker in text]
    return "; ".join(found) if found else None


def _extract_price_placeholder(text: str) -> str | None:
    placeholder = "Konkreter Preis abhängig vom Standort"
    return placeholder if placeholder in text else None


def _detect_stop_condition(text: str) -> str | None:
    stop_markers = {
        "Zeig uns, dass du ein Mensch bist": "bot protection challenge",
        "WAF Challenge": "bot protection challenge",
        "Enable JavaScript and cookies to continue": "bot protection challenge",
        "Anmelden": "login prompt",
        "Einloggen": "login prompt",
        "Zur Kasse": "checkout prompt",
    }
    for marker, reason in stop_markers.items():
        if marker in text:
            return reason
    return None


def _guess_brand(name: str) -> str | None:
    known_prefixes = ["REWE Bio", "REWE Beste Wahl", "ja!"]
    for prefix in known_prefixes:
        if name.startswith(prefix):
            return prefix

    words = name.split()
    return words[0] if len(words) > 1 else None


def _source_id_from_url(url: str) -> str | None:
    path = urlparse(url).path.rstrip("/")
    match = re.search(r"/(\d+)$", path)
    return match.group(1) if match else None


def _canonical_product_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed._replace(params="", query="", fragment="").geturl()


def _is_rewe_url(url: str) -> bool:
    return urlparse(url).netloc.endswith("rewe.de")


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()
