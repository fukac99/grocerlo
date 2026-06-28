"""Data quality checks for raw grocery product records."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable, Mapping

from app.normalization import parse_eur_price, parse_unit_price

MAX_REASONABLE_PRICE = Decimal("1000")
MAX_REASONABLE_UNIT_PRICE = Decimal("500")


@dataclass(frozen=True)
class RawProductQualityIssue:
    code: str
    message: str
    product_index: int
    field: str
    source_product_id: str | None = None
    retailer: str | None = None
    country: str | None = None


def check_raw_products(
    products: Iterable[Any],
    *,
    max_reasonable_price: Decimal = MAX_REASONABLE_PRICE,
    max_reasonable_unit_price: Decimal = MAX_REASONABLE_UNIT_PRICE,
) -> list[RawProductQualityIssue]:
    """Check raw scraper payloads or stored raw product objects for common defects."""
    indexed_products = list(enumerate(products))
    issues: list[RawProductQualityIssue] = []

    for index, product in indexed_products:
        issues.extend(
            _check_required_fields(
                index=index,
                product=product,
                max_reasonable_price=max_reasonable_price,
                max_reasonable_unit_price=max_reasonable_unit_price,
            )
        )

    issues.extend(_check_duplicate_source_ids(indexed_products))
    return issues


def _check_required_fields(
    *,
    index: int,
    product: Any,
    max_reasonable_price: Decimal,
    max_reasonable_unit_price: Decimal,
) -> list[RawProductQualityIssue]:
    issues: list[RawProductQualityIssue] = []

    if _is_blank(_value(product, "name", "raw_name")):
        issues.append(
            _issue(
                "missing_name",
                "Product is missing a name.",
                index,
                product,
                "name",
            )
        )

    if _is_blank(_value(product, "source_url")):
        issues.append(
            _issue(
                "missing_source_url",
                "Product is missing a source URL.",
                index,
                product,
                "source_url",
            )
        )

    price_text = _text(_value(product, "price", "raw_price"))
    if _is_blank(price_text):
        issues.append(
            _issue(
                "missing_price",
                "Product is missing a price.",
                index,
                product,
                "price",
            )
        )
    else:
        price = parse_eur_price(price_text)
        if price is None or price <= 0 or price > max_reasonable_price:
            issues.append(
                _issue(
                    "suspicious_price",
                    f"Product price looks suspicious: {price_text!r}.",
                    index,
                    product,
                    "price",
                )
            )

    unit_price_text = _text(_value(product, "unit_price", "raw_unit_price"))
    if not _is_blank(unit_price_text):
        unit_price = parse_unit_price(unit_price_text)
        if (
            unit_price is None
            or unit_price.price_per_base_unit <= 0
            or unit_price.price_per_base_unit > max_reasonable_unit_price
        ):
            issues.append(
                _issue(
                    "suspicious_unit_price",
                    f"Product unit price looks suspicious: {unit_price_text!r}.",
                    index,
                    product,
                    "unit_price",
                )
            )

    return issues


def _check_duplicate_source_ids(
    indexed_products: list[tuple[int, Any]],
) -> list[RawProductQualityIssue]:
    source_id_groups: dict[tuple[str | None, str | None, str], list[tuple[int, Any]]] = {}

    for index, product in indexed_products:
        source_product_id = _text(_value(product, "source_product_id"))
        if _is_blank(source_product_id):
            continue

        key = (
            _text(_value(product, "retailer")),
            _text(_value(product, "country")),
            source_product_id,
        )
        source_id_groups.setdefault(key, []).append((index, product))

    issues: list[RawProductQualityIssue] = []
    for (_retailer, _country, source_product_id), duplicates in source_id_groups.items():
        if len(duplicates) < 2:
            continue

        for index, product in duplicates:
            issues.append(
                _issue(
                    "duplicate_source_product_id",
                    f"Source product ID is duplicated: {source_product_id!r}.",
                    index,
                    product,
                    "source_product_id",
                )
            )

    return issues


def _issue(
    code: str,
    message: str,
    product_index: int,
    product: Any,
    field: str,
) -> RawProductQualityIssue:
    return RawProductQualityIssue(
        code=code,
        message=message,
        product_index=product_index,
        field=field,
        source_product_id=_text(_value(product, "source_product_id")),
        retailer=_text(_value(product, "retailer")),
        country=_text(_value(product, "country")),
    )


def _value(product: Any, *names: str) -> Any:
    if isinstance(product, Mapping):
        for name in names:
            if name in product:
                return product[name]
        return None

    for name in names:
        if hasattr(product, name):
            return getattr(product, name)
    return None


def _text(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip()


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    return str(value).strip() == ""


__all__ = [
    "MAX_REASONABLE_PRICE",
    "MAX_REASONABLE_UNIT_PRICE",
    "RawProductQualityIssue",
    "check_raw_products",
]
