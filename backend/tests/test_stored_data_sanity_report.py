import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from stored_data_sanity_report import build_sanity_report, validate_positive_limit  # noqa: E402


@dataclass(frozen=True)
class StoredScrapeRun:
    id: int
    retailer: str
    country: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    source_url: str


@dataclass(frozen=True)
class StoredRawProduct:
    id: int
    scrape_run_id: int
    retailer: str
    country: str
    source_product_id: str | None
    source_url: str | None
    raw_name: str | None
    raw_price: str | None
    raw_unit_price: str | None
    raw_package_size: str | None


def test_build_sanity_report_summarizes_counts_and_bad_row_identifiers() -> None:
    scrape_run = StoredScrapeRun(
        id=42,
        retailer="billa",
        country="AT",
        status="succeeded",
        started_at=datetime(2026, 6, 28, 18, 0, tzinfo=UTC),
        finished_at=None,
        source_url="https://shop.billa.at/kategorie",
    )
    raw_products = [
        StoredRawProduct(
            id=100,
            scrape_run_id=42,
            retailer="billa",
            country="AT",
            source_product_id="duplicate",
            source_url="https://shop.billa.at/produkte/duplicate-a",
            raw_name="Duplicate A",
            raw_price="1,49 €",
            raw_unit_price="1 kg 1,49 €",
            raw_package_size="1 kg",
        ),
        StoredRawProduct(
            id=101,
            scrape_run_id=42,
            retailer="billa",
            country="AT",
            source_product_id="duplicate",
            source_url="https://shop.billa.at/produkte/duplicate-b",
            raw_name="Duplicate B",
            raw_price="2,49 €",
            raw_unit_price="1 kg 2,49 €",
            raw_package_size=None,
        ),
        StoredRawProduct(
            id=102,
            scrape_run_id=42,
            retailer="billa",
            country="AT",
            source_product_id=None,
            source_url=" ",
            raw_name="",
            raw_price="0,00 €",
            raw_unit_price="per bunch",
            raw_package_size=None,
        ),
    ]

    report = build_sanity_report(scrape_run, raw_products, max_issues=10)

    assert report["scrape_run"] == {
        "id": 42,
        "retailer": "billa",
        "country": "AT",
        "status": "succeeded",
        "started_at": "2026-06-28T18:00:00+00:00",
        "finished_at": None,
        "source_url": "https://shop.billa.at/kategorie",
    }
    assert report["counts"]["raw_products"] == 3
    assert report["counts"]["missing_fields"] == {
        "source_product_id": 1,
        "source_url": 1,
        "raw_name": 1,
        "raw_price": 0,
        "raw_unit_price": 0,
        "raw_package_size": 2,
    }
    assert report["counts"]["issues_by_code"] == {
        "duplicate_source_product_id": 2,
        "missing_name": 1,
        "missing_source_url": 1,
        "suspicious_price": 1,
        "suspicious_unit_price": 1,
    }
    assert {
        (row["code"], row["raw_product_id"], row["source_product_id"])
        for row in report["bad_rows"]
    } == {
        ("duplicate_source_product_id", 100, "duplicate"),
        ("duplicate_source_product_id", 101, "duplicate"),
        ("missing_name", 102, None),
        ("missing_source_url", 102, None),
        ("suspicious_price", 102, None),
        ("suspicious_unit_price", 102, None),
    }
    assert report["bad_rows_truncated"] == 0


def test_build_sanity_report_truncates_bad_rows() -> None:
    scrape_run = StoredScrapeRun(
        id=43,
        retailer="billa",
        country="AT",
        status="succeeded",
        started_at=datetime(2026, 6, 28, 18, 0, tzinfo=UTC),
        finished_at=None,
        source_url="https://shop.billa.at/kategorie",
    )
    raw_products = [
        StoredRawProduct(
            id=200,
            scrape_run_id=43,
            retailer="billa",
            country="AT",
            source_product_id=None,
            source_url=None,
            raw_name=None,
            raw_price=None,
            raw_unit_price=None,
            raw_package_size=None,
        )
    ]

    report = build_sanity_report(scrape_run, raw_products, max_issues=2)

    assert len(report["bad_rows"]) == 2
    assert report["bad_rows_truncated"] == 1


def test_validate_positive_limit_rejects_negative_values() -> None:
    try:
        validate_positive_limit("--max-issues", -1)
    except SystemExit as exc:
        assert str(exc) == "--max-issues must be at least 1."
    else:
        raise AssertionError("Expected negative --max-issues to exit")
