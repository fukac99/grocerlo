import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from normalize_once import build_mpreis_report_only_normalization_report, parse_args  # noqa: E402


@dataclass(frozen=True)
class StoredRawProduct:
    id: int = 10
    retailer: str = "mpreis"
    country: str = "AT"
    source_product_id: str | None = "500167"
    source_url: str | None = (
        "https://www.mpreis.at/shop/p/bio-vom-berg-bio-eier-ml-6er-packung-500167"
    )
    raw_name: str | None = "BIO vom BERG Bio Eier M/L 6er-Packung"
    raw_brand: str | None = "BIO vom BERG"
    raw_category: str | None = "Schneller erster Einkauf"
    raw_price: str | None = "3,59 €"
    raw_old_price: str | None = None
    raw_unit_price: str | None = "0,60 € /Stk"
    raw_package_size: str | None = "6STK"
    raw_currency: str | None = "EUR"
    raw_availability: str | None = "Noch kein Markt gewählt"
    raw_promotion_text: str | None = "NUR MIT APP"
    raw_payload_json: dict[str, object] = field(
        default_factory=lambda: {"location_context": "no_market_selected"}
    )
    scraped_at: datetime = datetime(2026, 6, 29, 8, 0, tzinfo=UTC)


def test_mpreis_report_only_output_is_non_comparable_and_does_not_create_rows() -> None:
    report = build_mpreis_report_only_normalization_report(
        scrape_run_id=4,
        raw_products=[StoredRawProduct()],
    )

    assert report["mode"] == "report_only"
    assert report["comparison_eligibility"] == "non_comparable_validation_data"
    assert report["creates_retailer_products"] is False
    assert report["guardrails"] == {
        "scraping_performed": False,
        "matching_allowed": False,
        "comparison_api_or_ui_allowed": False,
        "requires_market_policy_before_downstream_use": True,
    }
    assert report["counts"]["raw_products"] == 1
    assert report["counts"]["rows_with_app_only_label"] == 1
    assert report["counts"]["rows_without_no_market_context"] == 0

    row = report["rows"][0]
    assert row["app_only_label_present"] is True
    assert row["app_only_label_source"] == "raw_promotion_text"
    assert row["normalized"]["package_quantity"] == "6"
    assert row["normalized"]["package_unit"] == "piece"
    assert row["normalized"]["normalized_quantity_base"] == "6"
    assert row["normalized"]["normalized_unit_base"] == "piece"
    assert row["normalized"]["unit_price_amount"] == "0.60"
    assert row["normalized"]["unit_price_unit"] == "piece"
    assert row["normalized"]["price_per_base_unit"] == "0.60"


def test_mpreis_report_flags_missing_fields_skips_and_suspicious_context() -> None:
    report = build_mpreis_report_only_normalization_report(
        scrape_run_id=4,
        raw_products=[
            StoredRawProduct(
                id=11,
                source_product_id=None,
                source_url=" ",
                raw_name=" ",
                raw_price="0,00 €",
                raw_unit_price=None,
                raw_package_size=None,
                raw_promotion_text=None,
                raw_payload_json={"location_context": "market_selected"},
            )
        ],
    )

    assert report["counts"]["missing_key_fields"] == {
        "source_product_id": 1,
        "source_url": 1,
        "raw_name": 1,
        "raw_price": 0,
        "raw_unit_price": 1,
        "raw_package_size": 1,
    }
    assert report["skipped_rows"] == [
        {"raw_product_id": 11, "reason": "raw product is missing a name"}
    ]
    assert {
        (value["raw_product_id"], value["field"], value["reason"])
        for value in report["suspicious_values"]
    } == {
        (11, "location_context", "unexpected MPREIS validation context"),
    }


def test_mpreis_requires_report_only_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["normalize_once.py", "4", "--retailer", "mpreis"])

    with pytest.raises(SystemExit):
        parse_args()


def test_report_only_guard_is_mpreis_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["normalize_once.py", "3", "--retailer", "billa", "--report-only"])

    with pytest.raises(SystemExit):
        parse_args()
