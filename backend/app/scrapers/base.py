from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class Category:
    name: str
    url: str
    source_id: str | None = None
    parent_name: str | None = None


@dataclass(frozen=True)
class RawProductPayload:
    retailer: str
    country: str
    source_url: str
    source_product_id: str | None = None
    name: str | None = None
    brand: str | None = None
    category: str | None = None
    price: str | None = None
    old_price: str | None = None
    unit_price: str | None = None
    package_size: str | None = None
    currency: str | None = None
    availability: str | None = None
    promotion_text: str | None = None
    raw_payload: dict[str, Any] = field(default_factory=dict)


class RetailerScraper(Protocol):
    retailer: str
    country: str

    async def scrape_categories(self) -> list[Category]:
        """Discover product category pages for this retailer."""

    async def scrape_products(self, category: Category) -> list[RawProductPayload]:
        """Extract raw product data for one category without interpreting it."""
