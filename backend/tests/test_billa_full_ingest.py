import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from app.scrapers import Category, RawProductPayload  # noqa: E402
from billa_full_ingest import (  # noqa: E402
    BROAD_RUN_CONFIRMATION,
    build_run_summary,
    effective_category_limit,
    is_broad_run,
    parse_args,
    select_categories,
    validate_args,
)


def test_default_run_is_limited_dry_run() -> None:
    args = parse_args([])

    validate_args(args)

    assert effective_category_limit(args) == 1
    assert args.max_products == 10
    assert not args.store
    assert not is_broad_run(args)


def test_broad_run_requires_exact_confirmation() -> None:
    args = parse_args(["--all-categories"])

    try:
        validate_args(args)
    except SystemExit as exc:
        assert "requires explicit confirmation" in str(exc)
    else:
        raise AssertionError("Expected unconfirmed broad run to exit")


def test_confirmed_broad_run_accepts_unlimited_products() -> None:
    args = parse_args(
        [
            "--store",
            "--all-categories",
            "--max-products",
            "0",
            "--confirm-broad-run",
            BROAD_RUN_CONFIRMATION,
        ]
    )

    validate_args(args)

    assert effective_category_limit(args) is None
    assert is_broad_run(args)


def test_select_categories_resumes_after_source_id_and_applies_limit() -> None:
    categories = [
        Category(name="Obst", url="https://example.test/obst", source_id="obst"),
        Category(name="Milch", url="https://example.test/milch", source_id="milch"),
        Category(name="Brot", url="https://example.test/brot", source_id="brot"),
    ]

    selected = select_categories(
        categories,
        start_category_index=0,
        resume_after_source_id="obst",
        resume_after_name=None,
        limit_categories=1,
    )

    assert [category.original_index for category in selected] == [1]
    assert [category.category.name for category in selected] == ["Milch"]


def test_build_run_summary_includes_dry_run_quality_and_samples() -> None:
    args = parse_args(["--sample-products", "1"])
    validate_args(args)
    category = Category(name="Obst", url="https://example.test/obst", source_id="obst")
    product = RawProductPayload(
        retailer="billa",
        country="AT",
        source_product_id="apple",
        source_url="https://example.test/apple",
        name="Apfel",
        price="1,99 €",
        unit_price="1 kg 1,99 €",
    )

    summary = build_run_summary(
        args=args,
        discovered_categories=[category],
        selected_categories=[],
        category_results=[],
        products=[product],
        scrape_run_id=None,
        run_status="succeeded",
        sanity_report=None,
    )

    assert summary["mode"] == "dry_run"
    assert summary["dry_run_quality"]["quality_issues"] == 0
    assert summary["sample_products"] == [
        {
            "retailer": "billa",
            "country": "AT",
            "source_url": "https://example.test/apple",
            "source_product_id": "apple",
            "name": "Apfel",
            "brand": None,
            "category": None,
            "price": "1,99 €",
            "old_price": None,
            "unit_price": "1 kg 1,99 €",
            "package_size": None,
            "currency": None,
            "availability": None,
            "promotion_text": None,
            "raw_payload": {},
        }
    ]
