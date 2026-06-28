"""Normalization utilities for scraped grocery data."""

from dataclasses import dataclass
from decimal import Decimal
import re


@dataclass(frozen=True)
class PackageSize:
    quantity: Decimal
    unit: str
    normalized_quantity: Decimal
    normalized_unit: str


@dataclass(frozen=True)
class UnitPrice:
    reference_quantity: Decimal
    reference_unit: str
    price_amount: Decimal
    currency: str
    normalized_reference_quantity: Decimal
    normalized_reference_unit: str
    price_per_base_unit: Decimal


_DECIMAL_NUMBER_PATTERN = r"\d+(?:[.,]\d+)?"
_UNIT_PATTERN = (
    r"packung|liter|litre|stück|stueck|piece|pieces|stk|kg|g|ml|lt|l"
)

_PACKAGE_SIZE_RE = re.compile(
    rf"\b(?P<quantity>{_DECIMAL_NUMBER_PATTERN})\s*(?P<unit>{_UNIT_PATTERN})\b",
    re.IGNORECASE,
)
_UNIT_PRICE_RE = re.compile(
    rf"\b(?:per\s+)?(?P<quantity>{_DECIMAL_NUMBER_PATTERN})\s*"
    rf"(?P<unit>{_UNIT_PATTERN})\s+"
    rf"(?P<price>{_DECIMAL_NUMBER_PATTERN})\s*(?P<currency>€|EUR)",
    re.IGNORECASE,
)
_EUR_PRICE_RE = re.compile(
    rf"\b(?P<amount>{_DECIMAL_NUMBER_PATTERN})\s*(?P<currency>€|EUR)",
    re.IGNORECASE,
)

_UNIT_ALIASES = {
    "kg": "kg",
    "g": "g",
    "l": "l",
    "lt": "l",
    "liter": "l",
    "litre": "l",
    "ml": "ml",
    "stk": "piece",
    "stueck": "piece",
    "stück": "piece",
    "piece": "piece",
    "pieces": "piece",
    "packung": "piece",
}

_BASE_UNIT_FACTORS = {
    "kg": ("kg", Decimal("1")),
    "g": ("kg", Decimal("0.001")),
    "l": ("l", Decimal("1")),
    "ml": ("l", Decimal("0.001")),
    "piece": ("piece", Decimal("1")),
}


def parse_eur_price(value: str | None) -> Decimal | None:
    """Parse simple EUR price strings such as ``2,39 €`` or ``2,39 EUR``."""
    if not value:
        return None

    match = _EUR_PRICE_RE.search(_normalize_spaces(value))
    if not match:
        return None

    return _parse_decimal(match.group("amount"))


def parse_package_size(value: str | None) -> PackageSize | None:
    """Parse package sizes and normalize them to kg, l, or piece where possible."""
    if not value:
        return None

    match = _PACKAGE_SIZE_RE.search(_normalize_spaces(value))
    if not match:
        return None

    quantity = _parse_decimal(match.group("quantity"))
    unit = _canonical_unit(match.group("unit"))
    return normalize_package_size(quantity, unit)


def normalize_package_size(quantity: Decimal, unit: str) -> PackageSize | None:
    canonical_unit = _canonical_unit(unit)
    base = _BASE_UNIT_FACTORS.get(canonical_unit)
    if base is None:
        return None

    normalized_unit, factor = base
    return PackageSize(
        quantity=quantity,
        unit=canonical_unit,
        normalized_quantity=quantity * factor,
        normalized_unit=normalized_unit,
    )


def parse_unit_price(value: str | None) -> UnitPrice | None:
    """Parse simple unit price strings such as ``100 g 1,25 €``."""
    if not value:
        return None

    match = _UNIT_PRICE_RE.search(_normalize_spaces(value))
    if not match:
        return None

    package_size = normalize_package_size(
        _parse_decimal(match.group("quantity")),
        match.group("unit"),
    )
    if package_size is None or package_size.normalized_quantity == 0:
        return None

    price_amount = _parse_decimal(match.group("price"))
    return UnitPrice(
        reference_quantity=package_size.quantity,
        reference_unit=package_size.unit,
        price_amount=price_amount,
        currency="EUR",
        normalized_reference_quantity=package_size.normalized_quantity,
        normalized_reference_unit=package_size.normalized_unit,
        price_per_base_unit=price_amount / package_size.normalized_quantity,
    )


def _parse_decimal(value: str) -> Decimal:
    return Decimal(value.strip().replace(",", "."))


def _canonical_unit(value: str) -> str:
    unit = value.strip().casefold().rstrip(".")
    return _UNIT_ALIASES.get(unit, unit)


def _normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


from app.normalization.retailer_products import (  # noqa: E402
    RawProductLike,
    RawProductNormalizationError,
    RetailerProductFields,
    normalize_raw_product_to_retailer_product,
)


__all__ = [
    "PackageSize",
    "RawProductLike",
    "RawProductNormalizationError",
    "RetailerProductFields",
    "UnitPrice",
    "normalize_package_size",
    "normalize_raw_product_to_retailer_product",
    "parse_eur_price",
    "parse_package_size",
    "parse_unit_price",
]
