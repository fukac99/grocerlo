from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.normalization import (
    RawProductNormalizationError,
    normalize_package_size,
    normalize_raw_product_to_retailer_product,
    parse_eur_price,
    parse_package_size,
    parse_unit_price,
)


@dataclass(frozen=True)
class StoredRawProduct:
    id: int = 10
    retailer: str = "billa"
    country: str = "AT"
    source_product_id: str | None = "produkte/billa-bio-milch"
    source_url: str | None = "https://shop.billa.at/produkte/billa-bio-milch"
    raw_name: str | None = " BILLA Bio Milch  "
    raw_brand: str | None = "BILLA Bio"
    raw_category: str | None = "Milchprodukte"
    raw_price: str | None = "2,39"
    raw_old_price: str | None = None
    raw_unit_price: str | None = "1 Liter 2,39 €"
    raw_package_size: str | None = "1 liter"
    raw_currency: str | None = "EUR"
    raw_availability: str | None = "online"
    raw_promotion_text: str | None = None
    scraped_at: datetime = datetime(2026, 6, 28, 18, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("raw_price", "expected"),
    [
        ("2,39 €", Decimal("2.39")),
        ("2,39 EUR", Decimal("2.39")),
        ("  2,39   €  ", Decimal("2.39")),
    ],
)
def test_parse_eur_price(raw_price: str, expected: Decimal) -> None:
    assert parse_eur_price(raw_price) == expected


@pytest.mark.parametrize(
    ("raw_size", "quantity", "unit", "base_quantity", "base_unit"),
    [
        ("500 g", Decimal("500"), "g", Decimal("0.500"), "kg"),
        ("1 kg", Decimal("1"), "kg", Decimal("1"), "kg"),
        ("1,5 liter", Decimal("1.5"), "l", Decimal("1.5"), "l"),
        ("250 ml", Decimal("250"), "ml", Decimal("0.250"), "l"),
        ("10 stk", Decimal("10"), "piece", Decimal("10"), "piece"),
    ],
)
def test_parse_package_size(
    raw_size: str,
    quantity: Decimal,
    unit: str,
    base_quantity: Decimal,
    base_unit: str,
) -> None:
    package_size = parse_package_size(raw_size)

    assert package_size is not None
    assert package_size.quantity == quantity
    assert package_size.unit == unit
    assert package_size.normalized_quantity == base_quantity
    assert package_size.normalized_unit == base_unit


def test_normalize_package_size_accepts_decimal_input() -> None:
    package_size = normalize_package_size(Decimal("1500"), "g")

    assert package_size is not None
    assert package_size.normalized_quantity == Decimal("1.500")
    assert package_size.normalized_unit == "kg"


@pytest.mark.parametrize(
    ("raw_unit_price", "base_unit", "base_price"),
    [
        ("1 kg 7,98 €", "kg", Decimal("7.98")),
        ("100 g 1,25 €", "kg", Decimal("12.5")),
        ("1 Liter 1,89 €", "l", Decimal("1.89")),
    ],
)
def test_parse_unit_price(raw_unit_price: str, base_unit: str, base_price: Decimal) -> None:
    unit_price = parse_unit_price(raw_unit_price)

    assert unit_price is not None
    assert unit_price.currency == "EUR"
    assert unit_price.normalized_reference_unit == base_unit
    assert unit_price.price_per_base_unit == base_price


def test_normalize_raw_product_to_retailer_product_preserves_source_references() -> None:
    retailer_product = normalize_raw_product_to_retailer_product(StoredRawProduct())

    assert retailer_product.raw_product_id == 10
    assert retailer_product.source_product_id == "produkte/billa-bio-milch"
    assert retailer_product.product_url == "https://shop.billa.at/produkte/billa-bio-milch"
    assert retailer_product.name == "BILLA Bio Milch"
    assert retailer_product.brand == "BILLA Bio"
    assert retailer_product.category == "Milchprodukte"
    assert retailer_product.observed_at == datetime(2026, 6, 28, 18, 0, tzinfo=UTC)


def test_normalize_raw_product_to_retailer_product_handles_price_and_package_fields() -> None:
    retailer_product = normalize_raw_product_to_retailer_product(
        StoredRawProduct(
            raw_price="2,49",
            raw_unit_price="100 g 1,25 €",
            raw_package_size="500 g",
        )
    )

    assert retailer_product.price_amount == Decimal("2.49")
    assert retailer_product.currency == "EUR"
    assert retailer_product.unit_price_amount == Decimal("1.25")
    assert retailer_product.unit_price_unit == "100 g"
    assert retailer_product.package_quantity == Decimal("500")
    assert retailer_product.package_unit == "g"
    assert retailer_product.normalized_quantity_base == Decimal("0.500")
    assert retailer_product.normalized_unit_base == "kg"
    assert retailer_product.price_per_base_unit == Decimal("12.5")


def test_normalize_raw_product_to_retailer_product_derives_base_price_from_package() -> None:
    retailer_product = normalize_raw_product_to_retailer_product(
        StoredRawProduct(raw_price="2,00", raw_unit_price=None, raw_package_size="500 g")
    )

    assert retailer_product.price_per_base_unit == Decimal("4.0")


def test_normalize_raw_product_to_retailer_product_marks_promotions() -> None:
    retailer_product = normalize_raw_product_to_retailer_product(
        StoredRawProduct(raw_old_price="2,99 €", raw_promotion_text="in Aktion")
    )

    assert retailer_product.is_promotion is True
    assert retailer_product.promotion_type == "old_price"


def test_normalize_raw_product_to_retailer_product_requires_name() -> None:
    with pytest.raises(RawProductNormalizationError, match="missing a name"):
        normalize_raw_product_to_retailer_product(StoredRawProduct(raw_name=" "))
