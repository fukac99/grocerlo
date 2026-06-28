import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright

from app.scrapers.base import Category, RawProductPayload


class BillaScraper:
    retailer = "billa"
    country = "AT"
    base_url = "https://shop.billa.at"
    category_url = "https://shop.billa.at/kategorie"

    def __init__(self, *, max_products_per_category: int = 30) -> None:
        self.max_products_per_category = max_products_per_category

    async def scrape_categories(self) -> list[Category]:
        html = await self._fetch_html(self.category_url)
        categories = self._parse_categories(html)
        return categories or [Category(name="Alle Kategorien", url=self.category_url, source_id="all")]

    async def scrape_products(self, category: Category) -> list[RawProductPayload]:
        html = await self._fetch_html(category.url)
        products = self._parse_products(html, category=category)
        return products[: self.max_products_per_category]

    async def _fetch_html(self, url: str) -> str:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            html = await page.content()
            await browser.close()
            return html

    def _parse_categories(self, html: str) -> list[Category]:
        soup = BeautifulSoup(html, "lxml")
        categories: list[Category] = []
        seen_urls: set[str] = set()

        for link in soup.find_all("a", href=True):
            href = str(link.get("href"))
            label = _clean_text(link.get_text(" ", strip=True))
            if not label or not _looks_like_category_label(label):
                continue

            url = _canonical_category_url(urljoin(self.base_url, href))
            if url is None or url in seen_urls:
                continue

            seen_urls.add(url)
            categories.append(
                Category(
                    name=_strip_trailing_count(label),
                    url=url,
                    source_id=_source_id_from_url(url),
                )
            )

        return categories

    def _parse_products(self, html: str, *, category: Category) -> list[RawProductPayload]:
        soup = BeautifulSoup(html, "lxml")
        products: list[RawProductPayload] = []
        seen_keys: set[str] = set()

        for heading in soup.find_all(["h2", "h3"]):
            name = _clean_text(heading.get_text(" ", strip=True))
            if not name or _is_non_product_heading(name):
                continue

            card = _nearest_product_card(heading)
            if card is None:
                continue

            card_text = _clean_text(card.get_text(" ", strip=True))
            prices = _extract_prices(card_text)
            if not prices:
                continue

            product_url = _extract_product_url(card, base_url=self.base_url)
            source_product_id = _source_id_from_url(product_url) if product_url else None
            dedupe_key = source_product_id or f"{name}:{prices[0]}:{category.name}"
            if dedupe_key in seen_keys:
                continue

            seen_keys.add(dedupe_key)
            products.append(
                RawProductPayload(
                    retailer=self.retailer,
                    country=self.country,
                    source_url=product_url or category.url,
                    source_product_id=source_product_id,
                    name=name,
                    brand=_guess_brand(name),
                    category=category.name,
                    price=prices[0],
                    old_price=prices[1] if len(prices) > 1 else None,
                    unit_price=_extract_unit_price(card_text),
                    package_size=_extract_package_size(card_text),
                    currency="EUR",
                    promotion_text=_extract_promotion_text(card_text),
                    raw_payload={
                        "category_url": category.url,
                        "card_text": card_text,
                    },
                )
            )

        return products


def _nearest_product_card(heading: Tag) -> Tag | None:
    for parent in heading.parents:
        if not isinstance(parent, Tag):
            continue

        text = _clean_text(parent.get_text(" ", strip=True))
        if "€" in text and len(text) < 2500:
            return parent

    return None


def _extract_product_url(card: Tag, *, base_url: str) -> str | None:
    for link in card.find_all("a", href=True):
        href = str(link.get("href"))
        if "/produkte/" in href or "/p/" in href:
            return urljoin(base_url, href)
    return None


def _extract_prices(text: str) -> list[str]:
    return re.findall(r"\d+,\d{2}\s*€", text)


def _extract_unit_price(text: str) -> str | None:
    patterns = [
        r"(?:1\s*(?:kg|l|liter|Liter|Stk|stk|Stück|stuck)\s+\d+,\d{2}\s*€)",
        r"(?:100\s*g\s+\d+,\d{2}\s*€)",
        r"(?:per\s+1\s*(?:kg|l)\s+\d+,\d{2}\s*€?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def _extract_package_size(text: str) -> str | None:
    patterns = [
        r"(?:Ab\s+)?\d+(?:,\d+)?\s*(?:kg|g|liter|Liter|l|ml|stk|Stk)\s+\w+",
        r"\d+(?:,\d+)?\s*(?:kg|g|liter|Liter|l|ml|stk|Stk)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def _extract_promotion_text(text: str) -> str | None:
    markers = ["in Aktion", "2+1", "1+1", "gratis", "ab 2", "Bei "]
    for marker in markers:
        index = text.find(marker)
        if index >= 0:
            return text[index : index + 160].strip()
    return None


def _guess_brand(name: str) -> str | None:
    known_prefixes = ["Ja! Natürlich", "BILLA Bio", "Clever", "Da komm ich her!"]
    for prefix in known_prefixes:
        if name.startswith(prefix):
            return prefix

    words = name.split()
    return words[0] if len(words) > 1 else None


def _looks_like_category_label(label: str) -> bool:
    if len(label) > 80:
        return False
    return bool(re.search(r"\d+$", label)) or label in {"Obst & Gemüse", "Getränke", "Tiefkühl"}


def _strip_trailing_count(label: str) -> str:
    return re.sub(r"\d+$", "", label).strip()


def _is_non_product_heading(name: str) -> bool:
    lowered = name.casefold()
    return lowered in {
        "alle kategorien",
        "pagination.headline",
    } or lowered.startswith("sortiert nach")


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _is_billa_url(url: str) -> bool:
    return urlparse(url).netloc.endswith("billa.at")


def _canonical_category_url(url: str) -> str | None:
    if not _is_billa_url(url):
        return None

    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if path == "/kategorie" or not path.startswith("/kategorie/"):
        return None

    slug = path.removeprefix("/kategorie/").strip("/")
    if not slug:
        return None

    return parsed._replace(path=path, params="", query="", fragment="").geturl()


def _source_id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    path = urlparse(url).path.strip("/")
    return path or None
