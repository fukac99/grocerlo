#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.quality import check_raw_products  # noqa: E402
from app.scrapers import BillaScraper, Category, RawProductPayload  # noqa: E402
from stored_data_sanity_report import load_sanity_report  # noqa: E402


BROAD_RUN_CONFIRMATION = "BILLA_FULL_INGEST"
DEFAULT_CATEGORY_LIMIT = 1


@dataclass(frozen=True)
class SelectedCategory:
    original_index: int
    category: Category


@dataclass(frozen=True)
class CategoryResult:
    original_index: int
    name: str
    source_id: str | None
    url: str
    status: str
    raw_products: int = 0
    error: str | None = None


async def main() -> None:
    args = parse_args()
    validate_args(args)

    try:
        summary = await run_ingest(args)
    except Exception as exc:
        raise SystemExit(f"BILLA ingest failed before a run summary could be produced: {exc}") from exc

    print(json.dumps(summary, ensure_ascii=False, indent=2))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a controlled operator-triggered BILLA ingest workflow."
    )
    parser.add_argument(
        "--store",
        action="store_true",
        help="Store scraped raw products in Postgres. Omit for a dry-run summary.",
    )
    parser.add_argument(
        "--all-categories",
        action="store_true",
        help="Scrape every discovered BILLA category. Requires broad-run confirmation.",
    )
    parser.add_argument(
        "--limit-categories",
        type=int,
        default=None,
        help=(
            "Maximum categories to scrape. Defaults to 1 unless --all-categories is set. "
            "Values above 1 require broad-run confirmation."
        ),
    )
    parser.add_argument(
        "--max-products",
        type=int,
        default=10,
        help="Maximum total raw products to scrape. Use 0 for no total cap.",
    )
    parser.add_argument(
        "--max-products-per-category",
        type=int,
        default=30,
        help="Maximum products to request from each category page.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=2.0,
        help="Seconds to wait between category product requests.",
    )
    parser.add_argument(
        "--start-category-index",
        type=int,
        default=0,
        help="Zero-based discovered-category index to start from when resuming.",
    )
    parser.add_argument(
        "--resume-after-source-id",
        default=None,
        help="Resume after the discovered category with this source_id.",
    )
    parser.add_argument(
        "--resume-after-name",
        default=None,
        help="Resume after the discovered category with this exact name.",
    )
    parser.add_argument(
        "--confirm-broad-run",
        default=None,
        metavar=BROAD_RUN_CONFIRMATION,
        help=f"Required exact token for multi-category or unlimited runs: {BROAD_RUN_CONFIRMATION}",
    )
    parser.add_argument(
        "--max-issues",
        type=int,
        default=50,
        help="Maximum quality/sanity bad-row details to include in output.",
    )
    parser.add_argument(
        "--sample-products",
        type=int,
        default=5,
        help="Number of scraped product payloads to include in dry-run output.",
    )
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    validate_non_negative_limit("--max-products", args.max_products)
    validate_non_negative_limit("--start-category-index", args.start_category_index)
    validate_non_negative_limit("--sample-products", args.sample_products)
    validate_positive_limit("--max-products-per-category", args.max_products_per_category)
    validate_positive_limit("--max-issues", args.max_issues)

    if args.limit_categories is not None:
        validate_positive_limit("--limit-categories", args.limit_categories)

    if args.delay_seconds < 0:
        raise SystemExit("--delay-seconds must be at least 0.")

    resume_options = [
        bool(args.start_category_index),
        args.resume_after_source_id is not None,
        args.resume_after_name is not None,
    ]
    if sum(resume_options) > 1:
        raise SystemExit(
            "Use only one resume option: --start-category-index, "
            "--resume-after-source-id, or --resume-after-name."
        )

    if is_broad_run(args) and args.confirm_broad_run != BROAD_RUN_CONFIRMATION:
        raise SystemExit(
            "Broad BILLA ingest requires explicit confirmation: "
            f"--confirm-broad-run {BROAD_RUN_CONFIRMATION}"
        )


def validate_positive_limit(name: str, value: int) -> None:
    if value < 1:
        raise SystemExit(f"{name} must be at least 1.")


def validate_non_negative_limit(name: str, value: int) -> None:
    if value < 0:
        raise SystemExit(f"{name} must be at least 0.")


def is_broad_run(args: argparse.Namespace) -> bool:
    category_limit = effective_category_limit(args)
    return args.all_categories or category_limit is None or category_limit > 1 or args.max_products == 0


def effective_category_limit(args: argparse.Namespace) -> int | None:
    if args.all_categories:
        return None
    return args.limit_categories or DEFAULT_CATEGORY_LIMIT


async def run_ingest(args: argparse.Namespace) -> dict[str, Any]:
    scraper = BillaScraper(max_products_per_category=args.max_products_per_category)
    discovered_categories = await scraper.scrape_categories()
    selected_categories = select_categories(
        discovered_categories,
        start_category_index=args.start_category_index,
        resume_after_source_id=args.resume_after_source_id,
        resume_after_name=args.resume_after_name,
        limit_categories=effective_category_limit(args),
    )

    products: list[RawProductPayload] = []
    category_results: list[CategoryResult] = []

    for selected in selected_categories:
        if reached_product_limit(products, args.max_products):
            break

        try:
            category_products = await scraper.scrape_products(selected.category)
        except Exception as exc:
            category_results.append(
                CategoryResult(
                    original_index=selected.original_index,
                    name=selected.category.name,
                    source_id=selected.category.source_id,
                    url=selected.category.url,
                    status="failed",
                    error=str(exc),
                )
            )
        else:
            limited_products = apply_remaining_product_limit(
                category_products,
                current_product_count=len(products),
                max_products=args.max_products,
            )
            products.extend(limited_products)
            category_results.append(
                CategoryResult(
                    original_index=selected.original_index,
                    name=selected.category.name,
                    source_id=selected.category.source_id,
                    url=selected.category.url,
                    status="succeeded",
                    raw_products=len(limited_products),
                )
            )

        if reached_product_limit(products, args.max_products):
            break
        if args.delay_seconds and selected != selected_categories[-1]:
            await asyncio.sleep(args.delay_seconds)

    scrape_run_id: int | None = None
    sanity_report: dict[str, Any] | None = None
    failed_categories = [result for result in category_results if result.status == "failed"]
    run_status = "failed" if failed_categories else "succeeded"
    error_message = summarize_category_errors(failed_categories)

    if args.store:
        scrape_run_id = await store_raw_products(
            products=products,
            source_url=scraper.category_url,
            status=run_status,
            error_message=error_message,
        )
        sanity_report = await load_stored_sanity_report(
            scrape_run_id=scrape_run_id,
            max_issues=args.max_issues,
        )

    return build_run_summary(
        args=args,
        discovered_categories=discovered_categories,
        selected_categories=selected_categories,
        category_results=category_results,
        products=products,
        scrape_run_id=scrape_run_id,
        run_status=run_status,
        sanity_report=sanity_report,
    )


def select_categories(
    categories: list[Category],
    *,
    start_category_index: int,
    resume_after_source_id: str | None,
    resume_after_name: str | None,
    limit_categories: int | None,
) -> list[SelectedCategory]:
    start_index = resolve_start_index(
        categories,
        start_category_index=start_category_index,
        resume_after_source_id=resume_after_source_id,
        resume_after_name=resume_after_name,
    )
    selected = [
        SelectedCategory(original_index=index, category=category)
        for index, category in enumerate(categories[start_index:], start=start_index)
    ]
    if limit_categories is not None:
        return selected[:limit_categories]
    return selected


def resolve_start_index(
    categories: list[Category],
    *,
    start_category_index: int,
    resume_after_source_id: str | None,
    resume_after_name: str | None,
) -> int:
    if resume_after_source_id is not None:
        for index, category in enumerate(categories):
            if category.source_id == resume_after_source_id:
                return index + 1
        raise SystemExit(f"No discovered BILLA category has source_id={resume_after_source_id!r}.")

    if resume_after_name is not None:
        for index, category in enumerate(categories):
            if category.name == resume_after_name:
                return index + 1
        raise SystemExit(f"No discovered BILLA category is named {resume_after_name!r}.")

    if start_category_index > len(categories):
        raise SystemExit(
            f"--start-category-index {start_category_index} exceeds "
            f"discovered category count {len(categories)}."
        )
    return start_category_index


def reached_product_limit(products: list[RawProductPayload], max_products: int) -> bool:
    return max_products > 0 and len(products) >= max_products


def apply_remaining_product_limit(
    category_products: list[RawProductPayload],
    *,
    current_product_count: int,
    max_products: int,
) -> list[RawProductPayload]:
    if max_products == 0:
        return category_products
    remaining = max(0, max_products - current_product_count)
    return category_products[:remaining]


async def store_raw_products(
    *,
    products: list[RawProductPayload],
    source_url: str,
    status: str,
    error_message: str | None,
) -> int:
    from app.db.session import async_session_factory
    from app.models.scraping import RawProduct, ScrapeRun, ScrapeRunStatus

    status_value = (
        ScrapeRunStatus.SUCCEEDED.value if status == "succeeded" else ScrapeRunStatus.FAILED.value
    )

    async with async_session_factory() as session:
        scrape_run = ScrapeRun(
            retailer="billa",
            country="AT",
            status=ScrapeRunStatus.RUNNING.value,
            source_url=source_url,
            scraper_version="0.1.0",
        )
        session.add(scrape_run)
        await session.flush()

        for product in products:
            session.add(
                RawProduct(
                    scrape_run_id=scrape_run.id,
                    retailer=product.retailer,
                    country=product.country,
                    source_product_id=product.source_product_id,
                    source_url=product.source_url,
                    raw_name=product.name,
                    raw_brand=product.brand,
                    raw_category=product.category,
                    raw_price=product.price,
                    raw_old_price=product.old_price,
                    raw_unit_price=product.unit_price,
                    raw_package_size=product.package_size,
                    raw_currency=product.currency,
                    raw_availability=product.availability,
                    raw_promotion_text=product.promotion_text,
                    raw_payload_json=product.raw_payload,
                )
            )

        scrape_run.status = status_value
        scrape_run.error_message = error_message
        scrape_run.finished_at = datetime.now(UTC)
        await session.commit()
        return scrape_run.id


async def load_stored_sanity_report(
    *,
    scrape_run_id: int,
    max_issues: int,
) -> dict[str, Any]:
    from app.db.session import async_session_factory

    async with async_session_factory() as session:
        return await load_sanity_report(
            session,
            scrape_run_id=scrape_run_id,
            retailer="billa",
            country="AT",
            max_issues=max_issues,
        )


def build_run_summary(
    *,
    args: argparse.Namespace,
    discovered_categories: list[Category],
    selected_categories: list[SelectedCategory],
    category_results: list[CategoryResult],
    products: list[RawProductPayload],
    scrape_run_id: int | None,
    run_status: str,
    sanity_report: dict[str, Any] | None,
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "retailer": "billa",
        "country": "AT",
        "status": run_status,
        "mode": "stored" if args.store else "dry_run",
        "broad_run_confirmed": is_broad_run(args),
        "limits": {
            "all_categories": args.all_categories,
            "limit_categories": effective_category_limit(args),
            "max_products": None if args.max_products == 0 else args.max_products,
            "max_products_per_category": args.max_products_per_category,
            "delay_seconds": args.delay_seconds,
        },
        "resume": {
            "start_category_index": args.start_category_index,
            "resume_after_source_id": args.resume_after_source_id,
            "resume_after_name": args.resume_after_name,
        },
        "counts": {
            "categories_discovered": len(discovered_categories),
            "categories_selected": len(selected_categories),
            "categories_attempted": len(category_results),
            "categories_succeeded": sum(1 for result in category_results if result.status == "succeeded"),
            "categories_failed": sum(1 for result in category_results if result.status == "failed"),
            "raw_products": len(products),
        },
        "categories": [asdict(result) for result in category_results],
        "storage": {
            "enabled": args.store,
            "scrape_run_id": scrape_run_id,
        },
    }

    if sanity_report is not None:
        summary["sanity_report"] = sanity_report
    else:
        summary["dry_run_quality"] = build_quality_summary(products, max_issues=args.max_issues)
        summary["sample_products"] = [asdict(product) for product in products[: args.sample_products]]

    return summary


def build_quality_summary(
    products: list[RawProductPayload],
    *,
    max_issues: int,
) -> dict[str, Any]:
    quality_issues = check_raw_products(products)
    issue_counts = Counter(issue.code for issue in quality_issues)
    return {
        "quality_issues": len(quality_issues),
        "issues_by_code": dict(sorted(issue_counts.items())),
        "bad_rows": [
            {
                "code": issue.code,
                "field": issue.field,
                "message": issue.message,
                "product_index": issue.product_index,
                "source_product_id": issue.source_product_id,
            }
            for issue in quality_issues[:max_issues]
        ],
        "bad_rows_truncated": max(0, len(quality_issues) - max_issues),
    }


def summarize_category_errors(failed_categories: list[CategoryResult]) -> str | None:
    if not failed_categories:
        return None
    messages = [
        f"{category.name} ({category.original_index}): {category.error}"
        for category in failed_categories[:5]
    ]
    remaining = len(failed_categories) - len(messages)
    if remaining > 0:
        messages.append(f"... and {remaining} more category errors")
    return "; ".join(messages)


if __name__ == "__main__":
    asyncio.run(main())
