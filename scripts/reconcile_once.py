#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.db.session import async_session_factory  # noqa: E402
from app.matching import (  # noqa: E402
    CANDIDATE_THRESHOLD,
    REVIEW_THRESHOLD,
    STRONG_MATCH_THRESHOLD,
    ReconciliationOptions,
    build_reconciliation_report,
)
from app.models import RetailerProduct  # noqa: E402

MAX_LIMIT_PER_RETAILER = 500


async def main() -> None:
    args = parse_args()
    validate_args(args)

    try:
        async with async_session_factory() as session:
            products = await load_retailer_products(
                session,
                country=args.country,
                retailers=args.retailer,
                limit_per_retailer=args.limit_per_retailer,
            )
    except SQLAlchemyError as exc:
        raise SystemExit(
            "Could not query normalized retailer products. Ensure local Postgres is running and "
            "migrations have been applied."
        ) from exc

    report = build_reconciliation_report(
        products,
        options=ReconciliationOptions(
            candidate_threshold=args.candidate_threshold,
            strong_threshold=args.strong_threshold,
            review_threshold=args.review_threshold,
            max_examples=args.max_examples,
        ),
    )
    report["selection"] = {
        "country": args.country,
        "retailers": args.retailer or "all",
        "limit_per_retailer": args.limit_per_retailer,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a read-only, one-off reconciliation report over normalized retailer products."
        )
    )
    parser.add_argument(
        "--country",
        default="AT",
        help="Country code for normalized retailer products.",
    )
    parser.add_argument(
        "--retailer",
        action="append",
        default=None,
        help="Retailer to include. Repeat to compare selected retailers; defaults to all.",
    )
    parser.add_argument(
        "--limit-per-retailer",
        type=int,
        default=100,
        help=f"Maximum normalized products to load per retailer, capped at {MAX_LIMIT_PER_RETAILER}.",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=20,
        help="Maximum scored examples to include for match-quality review.",
    )
    parser.add_argument(
        "--candidate-threshold",
        type=parse_decimal,
        default=CANDIDATE_THRESHOLD,
        help="Minimum score for candidate matches.",
    )
    parser.add_argument(
        "--strong-threshold",
        type=parse_decimal,
        default=STRONG_MATCH_THRESHOLD,
        help="Minimum score for strong candidate matches.",
    )
    parser.add_argument(
        "--review-threshold",
        type=parse_decimal,
        default=REVIEW_THRESHOLD,
        help="Minimum score for non-candidate review examples.",
    )
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    if args.limit_per_retailer < 1:
        raise SystemExit("--limit-per-retailer must be at least 1.")
    if args.limit_per_retailer > MAX_LIMIT_PER_RETAILER:
        raise SystemExit(
            f"--limit-per-retailer must be {MAX_LIMIT_PER_RETAILER} or lower for local runs."
        )
    if args.max_examples < 0:
        raise SystemExit("--max-examples must be zero or greater.")
    if args.review_threshold < 0:
        raise SystemExit("--review-threshold must be zero or greater.")
    if args.candidate_threshold <= args.review_threshold:
        raise SystemExit("--candidate-threshold must be greater than --review-threshold.")
    if args.strong_threshold <= args.candidate_threshold:
        raise SystemExit("--strong-threshold must be greater than --candidate-threshold.")


async def load_retailer_products(
    session,
    *,
    country: str,
    retailers: list[str] | None,
    limit_per_retailer: int,
) -> list[RetailerProduct]:
    selected_retailers = retailers or await discover_retailers(session, country=country)
    products: list[RetailerProduct] = []
    for retailer in selected_retailers:
        result = await session.scalars(
            select(RetailerProduct)
            .where(RetailerProduct.country == country, RetailerProduct.retailer == retailer)
            .order_by(RetailerProduct.observed_at.desc(), RetailerProduct.name, RetailerProduct.id)
            .limit(limit_per_retailer)
        )
        products.extend(result.all())
    return products


async def discover_retailers(session, *, country: str) -> list[str]:
    result = await session.scalars(
        select(RetailerProduct.retailer)
        .where(RetailerProduct.country == country)
        .distinct()
        .order_by(RetailerProduct.retailer)
    )
    return list(result.all())


def parse_decimal(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"invalid decimal value: {value}") from exc


if __name__ == "__main__":
    asyncio.run(main())
