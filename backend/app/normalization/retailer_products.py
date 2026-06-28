"""Normalize stored raw product rows into retailer product fields."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol

from app.normalization import PackageSize, UnitPrice, parse_eur_price, parse_package_size, parse_unit_price


class RawProductLike(Protocol):
    id: int
    retailer: str
    country: str
    source_product_id: str | None
    source_url: str | None
    raw_name: str | None
    raw_brand: str | None
    raw_category: str | None
    raw_price: str | None
    raw_old_price: str | None
    raw_unit_price: str | None
    raw_package_size: str | None
    raw_currency: str | None
    raw_availability: str | None
    raw_promotion_text: str | None
    scraped_at: datetime


@dataclass(frozen=True)
class RetailerProductFields:
    raw_product_id: int
    retailer: str
    country: str
    source_product_id: str | None
    product_url: str | None
    name: str
    brand: str | None
    category: str | None
    price_amount: Decimal | None
    currency: str | None
    unit_price_amount: Decimal | None
    unit_price_unit: str | None
    package_quantity: Decimal | None
    package_unit: str | None
    normalized_quantity_base: Decimal | None
    normalized_unit_base: str | None
    price_per_base_unit: Decimal | None
    is_promotion: bool
    promotion_type: str | None
    availability: str | None
    observed_at: datetime

    def as_model_kwargs(self) -> dict[str, object]:
        return self.__dict__.copy()


class RawProductNormalizationError(ValueError):
    """Raised when a raw row cannot produce a valid retailer product."""


def normalize_raw_product_to_retailer_product(
    raw_product: RawProductLike,
) -> RetailerProductFields:
    name = _clean_text(raw_product.raw_name)
    if name is None:
        raise RawProductNormalizationError("raw product is missing a name")

    package_size = parse_package_size(raw_product.raw_package_size)
    unit_price = parse_unit_price(raw_product.raw_unit_price)
    currency = _normalize_currency(raw_product.raw_currency, unit_price=unit_price)
    price_amount = _parse_price(raw_product.raw_price, currency=currency)

    return RetailerProductFields(
        raw_product_id=raw_product.id,
        retailer=raw_product.retailer,
        country=raw_product.country,
        source_product_id=_clean_text(raw_product.source_product_id),
        product_url=_clean_text(raw_product.source_url),
        name=name,
        brand=_clean_text(raw_product.raw_brand),
        category=_clean_text(raw_product.raw_category),
        price_amount=price_amount,
        currency=currency,
        unit_price_amount=unit_price.price_amount if unit_price else None,
        unit_price_unit=_format_unit_price_unit(unit_price),
        package_quantity=package_size.quantity if package_size else None,
        package_unit=package_size.unit if package_size else None,
        normalized_quantity_base=package_size.normalized_quantity if package_size else None,
        normalized_unit_base=package_size.normalized_unit if package_size else None,
        price_per_base_unit=_price_per_base_unit(price_amount, package_size, unit_price),
        is_promotion=_is_promotion(raw_product),
        promotion_type=_promotion_type(raw_product),
        availability=_clean_text(raw_product.raw_availability),
        observed_at=raw_product.scraped_at,
    )


def _parse_price(value: str | None, *, currency: str | None) -> Decimal | None:
    price = parse_eur_price(value)
    if price is not None or currency != "EUR" or value is None:
        return price
    return parse_eur_price(f"{value} EUR")


def _normalize_currency(value: str | None, *, unit_price: UnitPrice | None) -> str | None:
    if value:
        currency = value.strip().upper()
        if currency in {"€", "EUR"}:
            return "EUR"
        return currency
    return unit_price.currency if unit_price else None


def _price_per_base_unit(
    price_amount: Decimal | None,
    package_size: PackageSize | None,
    unit_price: UnitPrice | None,
) -> Decimal | None:
    if unit_price is not None:
        return unit_price.price_per_base_unit
    if price_amount is None or package_size is None or package_size.normalized_quantity == 0:
        return None
    return price_amount / package_size.normalized_quantity


def _is_promotion(raw_product: RawProductLike) -> bool:
    return _clean_text(raw_product.raw_old_price) is not None or _clean_text(
        raw_product.raw_promotion_text
    ) is not None


def _promotion_type(raw_product: RawProductLike) -> str | None:
    promotion_text = _clean_text(raw_product.raw_promotion_text)
    if _clean_text(raw_product.raw_old_price) is not None:
        return "old_price"
    if promotion_text is None:
        return None

    lowered = promotion_text.casefold()
    if any(marker in lowered for marker in ("2+1", "1+1", "gratis", "ab 2")):
        return "multi_buy"
    if "aktion" in lowered:
        return "discount"
    return "promotion"


def _format_unit_price_unit(unit_price: UnitPrice | None) -> str | None:
    if unit_price is None:
        return None
    if unit_price.reference_quantity == 1:
        return unit_price.reference_unit
    return f"{_format_decimal(unit_price.reference_quantity)} {unit_price.reference_unit}"


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split())
    return cleaned or None


def _format_decimal(value: Decimal) -> str:
    return format(value.normalize(), "f")


__all__ = [
    "RawProductLike",
    "RawProductNormalizationError",
    "RetailerProductFields",
    "normalize_raw_product_to_retailer_product",
]
