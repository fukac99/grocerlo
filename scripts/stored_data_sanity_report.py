#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.db.session import async_session_factory  # noqa: E402
from app.models.scraping import RawProduct, ScrapeRun  # noqa: E402
from app.quality import check_raw_products  # noqa: E402


async def main() -> None:
    args = parse_args()
    validate_positive_limit("--max-issues", args.max_issues)

    try:
        async with async_session_factory() as session:
            report = await load_sanity_report(
                session,
                scrape_run_id=args.scrape_run_id,
                retailer=args.retailer,
                country=args.country,
                max_issues=args.max_issues,
            )
    except SQLAlchemyError as exc:
        raise SystemExit(
            "Could not query stored scrape data. Ensure local Postgres is running and "
            "migrations have been applied."
        ) from exc

    print(json.dumps(report, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize stored raw products for the latest or selected scrape run."
    )
    parser.add_argument(
        "--scrape-run-id",
        type=int,
        default=None,
        help="Scrape run to inspect. Defaults to the latest matching run.",
    )
    parser.add_argument(
        "--retailer",
        choices=["billa", "mpreis"],
        default="billa",
        help="Retailer stored scrape runs to inspect.",
    )
    parser.add_argument(
        "--country",
        default="AT",
        help="Country code for latest-run lookup.",
    )
    parser.add_argument(
        "--max-issues",
        type=int,
        default=50,
        help="Maximum bad-row details to include.",
    )
    return parser.parse_args()


def validate_positive_limit(name: str, value: int) -> None:
    if value < 1:
        raise SystemExit(f"{name} must be at least 1.")


async def load_sanity_report(
    session: Any,
    *,
    scrape_run_id: int | None,
    retailer: str,
    country: str,
    max_issues: int,
) -> dict[str, Any]:
    scrape_run = await _load_scrape_run(
        session,
        scrape_run_id=scrape_run_id,
        retailer=retailer,
        country=country,
    )
    raw_products = list(
        (
            await session.scalars(
                select(RawProduct)
                .where(RawProduct.scrape_run_id == scrape_run.id)
                .order_by(RawProduct.id)
            )
        ).all()
    )
    return build_sanity_report(scrape_run, raw_products, max_issues=max_issues)


async def _load_scrape_run(
    session: Any,
    *,
    scrape_run_id: int | None,
    retailer: str,
    country: str,
) -> ScrapeRun:
    query = select(ScrapeRun).where(ScrapeRun.retailer == retailer)
    if scrape_run_id is not None:
        query = query.where(ScrapeRun.id == scrape_run_id)
    else:
        query = (
            query.where(ScrapeRun.country == country)
            .order_by(ScrapeRun.started_at.desc(), ScrapeRun.id.desc())
            .limit(1)
        )

    scrape_run = await session.scalar(query)
    if scrape_run is None:
        selector = f"id={scrape_run_id}" if scrape_run_id is not None else f"{retailer}/{country}"
        raise SystemExit(f"No stored scrape run found for {selector}.")
    return scrape_run


def build_sanity_report(
    scrape_run: Any,
    raw_products: list[Any],
    *,
    max_issues: int = 50,
) -> dict[str, Any]:
    quality_issues = check_raw_products(raw_products)
    issue_counts = Counter(issue.code for issue in quality_issues)

    return {
        "scrape_run": {
            "id": _value(scrape_run, "id"),
            "retailer": _value(scrape_run, "retailer"),
            "country": _value(scrape_run, "country"),
            "status": _value(scrape_run, "status"),
            "started_at": _json_value(_value(scrape_run, "started_at")),
            "finished_at": _json_value(_value(scrape_run, "finished_at")),
            "source_url": _value(scrape_run, "source_url"),
        },
        "counts": {
            "raw_products": len(raw_products),
            "quality_issues": len(quality_issues),
            "missing_fields": _missing_field_counts(raw_products),
            "issues_by_code": dict(sorted(issue_counts.items())),
        },
        "bad_rows": [
            _bad_row_payload(issue, raw_products[issue.product_index])
            for issue in quality_issues[:max_issues]
        ],
        "bad_rows_truncated": max(0, len(quality_issues) - max_issues),
    }


def _missing_field_counts(raw_products: list[Any]) -> dict[str, int]:
    fields = [
        "source_product_id",
        "source_url",
        "raw_name",
        "raw_price",
        "raw_unit_price",
        "raw_package_size",
    ]
    return {
        field: sum(1 for product in raw_products if _is_blank(_value(product, field)))
        for field in fields
    }


def _bad_row_payload(issue: Any, raw_product: Any) -> dict[str, Any]:
    return {
        "code": issue.code,
        "field": issue.field,
        "message": issue.message,
        "raw_product_id": _value(raw_product, "id"),
        "scrape_run_id": _value(raw_product, "scrape_run_id"),
        "source_product_id": _value(raw_product, "source_product_id"),
        "source_url": _value(raw_product, "source_url"),
        "raw_name": _value(raw_product, "raw_name"),
        "raw_price": _value(raw_product, "raw_price"),
        "raw_unit_price": _value(raw_product, "raw_unit_price"),
    }


def _value(obj: Any, name: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    return str(value).strip() == ""


def _json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


if __name__ == "__main__":
    asyncio.run(main())
