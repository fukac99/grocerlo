from dataclasses import dataclass
from decimal import Decimal

from app.quality import check_raw_products


@dataclass(frozen=True)
class RawProductPayload:
    retailer: str
    country: str
    source_url: str
    source_product_id: str | None = None
    name: str | None = None
    price: str | None = None
    unit_price: str | None = None


@dataclass(frozen=True)
class StoredRawProduct:
    retailer: str
    country: str
    source_url: str | None
    source_product_id: str | None
    raw_name: str | None
    raw_price: str | None
    raw_unit_price: str | None


def test_check_raw_products_accepts_clean_payloads() -> None:
    products = [
        RawProductPayload(
            retailer="billa",
            country="AT",
            source_product_id="123",
            source_url="https://shop.billa.at/products/123",
            name="Bio Milch",
            price="1,49 €",
            unit_price="1 l 1,49 €",
        )
    ]

    assert check_raw_products(products) == []


def test_check_raw_products_reports_missing_payload_fields() -> None:
    products = [
        RawProductPayload(
            retailer="billa",
            country="AT",
            source_url=" ",
            name="",
            price=None,
        )
    ]

    issues = check_raw_products(products)

    assert {issue.code for issue in issues} == {
        "missing_name",
        "missing_price",
        "missing_source_url",
    }
    assert all(issue.product_index == 0 for issue in issues)


def test_check_raw_products_reports_duplicate_source_ids_by_retailer_and_country() -> None:
    products = [
        RawProductPayload(
            retailer="billa",
            country="AT",
            source_product_id="duplicate",
            source_url="https://example.com/1",
            name="One",
            price="1,00 €",
        ),
        RawProductPayload(
            retailer="billa",
            country="AT",
            source_product_id="duplicate",
            source_url="https://example.com/2",
            name="Two",
            price="2,00 €",
        ),
        RawProductPayload(
            retailer="billa",
            country="DE",
            source_product_id="duplicate",
            source_url="https://example.com/3",
            name="Three",
            price="3,00 €",
        ),
    ]

    issues = check_raw_products(products)

    duplicate_issues = [issue for issue in issues if issue.code == "duplicate_source_product_id"]
    assert [issue.product_index for issue in duplicate_issues] == [0, 1]


def test_check_raw_products_reports_suspicious_prices_and_unit_prices() -> None:
    products = [
        RawProductPayload(
            retailer="billa",
            country="AT",
            source_product_id="zero",
            source_url="https://example.com/zero",
            name="Zero Price",
            price="0,00 €",
            unit_price="1 kg 0,00 €",
        ),
        RawProductPayload(
            retailer="billa",
            country="AT",
            source_product_id="huge",
            source_url="https://example.com/huge",
            name="Huge Price",
            price="1001,00 €",
            unit_price="100 g 99,99 €",
        ),
        RawProductPayload(
            retailer="billa",
            country="AT",
            source_product_id="bad",
            source_url="https://example.com/bad",
            name="Bad Price",
            price="call for price",
            unit_price="per bunch",
        ),
    ]

    issues = check_raw_products(products)

    assert [issue.code for issue in issues].count("suspicious_price") == 3
    assert [issue.code for issue in issues].count("suspicious_unit_price") == 3


def test_check_raw_products_accepts_stored_raw_product_shape() -> None:
    products = [
        StoredRawProduct(
            retailer="billa",
            country="AT",
            source_product_id="stored",
            source_url="https://shop.billa.at/products/stored",
            raw_name="Stored Product",
            raw_price="2,49 €",
            raw_unit_price="1 kg 2,49 €",
        )
    ]

    assert check_raw_products(products) == []


def test_check_raw_products_allows_custom_thresholds() -> None:
    products = [
        RawProductPayload(
            retailer="billa",
            country="AT",
            source_product_id="custom",
            source_url="https://example.com/custom",
            name="Custom Threshold",
            price="11,00 €",
            unit_price="1 kg 11,00 €",
        )
    ]

    issues = check_raw_products(
        products,
        max_reasonable_price=Decimal("10"),
        max_reasonable_unit_price=Decimal("10"),
    )

    assert {issue.code for issue in issues} == {
        "suspicious_price",
        "suspicious_unit_price",
    }
