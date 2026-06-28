from decimal import Decimal

import pytest

from app.normalization import (
    normalize_package_size,
    parse_eur_price,
    parse_package_size,
    parse_unit_price,
)


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
