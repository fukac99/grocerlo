#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.db import normalize_retailer_products_for_scrape_run  # noqa: E402
from app.db.session import async_session_factory  # noqa: E402
from app.models import RawProduct, ScrapeRun  # noqa: E402
from app.normalization import (  # noqa: E402
    RawProductNormalizationError,
    normalize_raw_product_to_retailer_product,
)
from sqlalchemy import select  # noqa: E402


MPREIS_APP_ONLY_MARKERS = ("nur mit app", "app coupon", "rabattsticker")
KEY_FIELDS = (
    "source_product_id",
    "source_url",
    "raw_name",
    "raw_price",
    "raw_unit_price",
    "raw_package_size",
)


class RawProductReportLike(Protocol):
    id: int
    retailer: str
    country: str
    source_product_id: str | None
    source_url: str | None
    raw_name: str | None
    raw_brand: str | None
    raw_category: str | None
    raw_price: str | None
    raw_old_price: str | None
    raw_unit_price: str | None
    raw_package_size: str | None
    raw_currency: str | None
    raw_availability: str | None
    raw_promotion_text: str | None
    raw_payload_json: dict[str, Any]
    scraped_at: Any


async def main() -> None:
    args = parse_args()
    async with async_session_factory() as session:
        if args.report_only:
            raw_products = await select_raw_products_for_report(
                session,
                scrape_run_id=args.scrape_run_id,
                retailer=args.retailer,
                limit=args.limit,
            )
            print(
                json.dumps(
                    build_mpreis_report_only_normalization_report(
                        scrape_run_id=args.scrape_run_id,
                        raw_products=raw_products,
                    ),
                    indent=2,
                )
            )
            return

        result = await normalize_retailer_products_for_scrape_run(
            session,
            scrape_run_id=args.scrape_run_id,
            retailer=args.retailer,
            limit=args.limit,
        )
        await session.commit()

    print(
        json.dumps(
            {
                "scrape_run_id": result.scrape_run_id,
                "retailer": result.retailer,
                "existing_retailer_products": result.existing,
                "created_retailer_products": result.created,
                "skipped_raw_products": [
                    {"raw_product_id": skipped.raw_product_id, "reason": skipped.reason}
                    for skipped in result.skipped
                ],
            },
            indent=2,
        )
    )


async def select_raw_products_for_report(
    session: Any,
    *,
    scrape_run_id: int,
    retailer: str,
    limit: int | None,
) -> list[RawProduct]:
    scrape_run = await session.get(ScrapeRun, scrape_run_id)
    if scrape_run is None:
        raise ValueError(f"scrape_run_id does not exist: {scrape_run_id}")

    statement = (
        select(RawProduct)
        .where(RawProduct.scrape_run_id == scrape_run_id, RawProduct.retailer == retailer)
        .order_by(RawProduct.id)
    )
    if limit is not None:
        statement = statement.limit(limit)

    result = await session.execute(statement)
    return list(result.scalars().all())


def build_mpreis_report_only_normalization_report(
    *,
    scrape_run_id: int,
    raw_products: list[RawProductReportLike],
) -> dict[str, Any]:
    rows = [_build_mpreis_report_row(raw_product) for raw_product in raw_products]
    missing_key_fields = {
        field: sum(1 for row in rows if field in row["missing_key_fields"]) for field in KEY_FIELDS
    }
    suspicious_values = [value for row in rows for value in row["suspicious_values"]]
    skipped_rows = [
        {"raw_product_id": row["raw_product_id"], "reason": row["skip_reason"]}
        for row in rows
        if row["skip_reason"] is not None
    ]

    return {
        "scrape_run_id": scrape_run_id,
        "retailer": "mpreis",
        "mode": "report_only",
        "comparison_eligibility": "non_comparable_validation_data",
        "creates_retailer_products": False,
        "guardrails": {
            "scraping_performed": False,
            "matching_allowed": False,
            "comparison_api_or_ui_allowed": False,
            "requires_market_policy_before_downstream_use": True,
        },
        "counts": {
            "raw_products": len(raw_products),
            "rows_with_app_only_label": sum(1 for row in rows if row["app_only_label_present"]),
            "rows_without_no_market_context": sum(
                1 for row in rows if row["location_context"] != "no_market_selected"
            ),
            "missing_key_fields": missing_key_fields,
            "skipped_rows": len(skipped_rows),
            "suspicious_values": len(suspicious_values),
        },
        "skipped_rows": skipped_rows,
        "suspicious_values": suspicious_values,
        "rows": rows,
    }


def _build_mpreis_report_row(raw_product: RawProductReportLike) -> dict[str, Any]:
    missing_key_fields = [field for field in KEY_FIELDS if _is_blank(getattr(raw_product, field))]
    suspicious_values: list[dict[str, Any]] = []
    skip_reason = None

    try:
        fields = normalize_raw_product_to_retailer_product(raw_product)
    except RawProductNormalizationError as exc:
        fields = None
        skip_reason = str(exc)

    price_amount = fields.price_amount if fields else None
    unit_price_amount = fields.unit_price_amount if fields else None
    price_per_base_unit = fields.price_per_base_unit if fields else None
    if price_amount is not None and (price_amount <= 0 or price_amount > Decimal("100")):
        suspicious_values.append(
            _suspicious_value(raw_product.id, "raw_price", price_amount, "outside expected range")
        )
    if unit_price_amount is not None and (
        unit_price_amount <= 0 or unit_price_amount > Decimal("1000")
    ):
        suspicious_values.append(
            _suspicious_value(
                raw_product.id,
                "raw_unit_price",
                unit_price_amount,
                "outside expected range",
            )
        )
    if _location_context(raw_product) != "no_market_selected":
        suspicious_values.append(
            _suspicious_value(
                raw_product.id,
                "location_context",
                _location_context(raw_product),
                "unexpected MPREIS validation context",
            )
        )

    return {
        "raw_product_id": raw_product.id,
        "source_product_id": _clean_text(raw_product.source_product_id),
        "name": _clean_text(raw_product.raw_name),
        "location_context": _location_context(raw_product),
        "app_only_label_present": _app_only_label_present(raw_product),
        "app_only_label_source": _app_only_label_source(raw_product),
        "missing_key_fields": missing_key_fields,
        "skip_reason": skip_reason,
        "suspicious_values": suspicious_values,
        "normalized": {
            "price_amount": _json_decimal(price_amount),
            "currency": fields.currency if fields else None,
            "package_quantity": _json_decimal(fields.package_quantity if fields else None),
            "package_unit": fields.package_unit if fields else None,
            "normalized_quantity_base": _json_decimal(
                fields.normalized_quantity_base if fields else None
            ),
            "normalized_unit_base": fields.normalized_unit_base if fields else None,
            "unit_price_amount": _json_decimal(unit_price_amount),
            "unit_price_unit": fields.unit_price_unit if fields else None,
            "price_per_base_unit": _json_decimal(price_per_base_unit),
            "is_promotion": fields.is_promotion if fields else None,
            "promotion_type": fields.promotion_type if fields else None,
        },
    }


def _suspicious_value(
    raw_product_id: int,
    field: str,
    value: object,
    reason: str,
) -> dict[str, Any]:
    return {
        "raw_product_id": raw_product_id,
        "field": field,
        "value": _json_decimal(value),
        "reason": reason,
    }


def _location_context(raw_product: RawProductReportLike) -> str | None:
    return raw_product.raw_payload_json.get("location_context")


def _app_only_label_present(raw_product: RawProductReportLike) -> bool:
    return _app_only_label_source(raw_product) is not None


def _app_only_label_source(raw_product: RawProductReportLike) -> str | None:
    promotion_text = _clean_text(raw_product.raw_promotion_text)
    if promotion_text and _has_app_only_marker(promotion_text):
        return "raw_promotion_text"

    payload_text = json.dumps(raw_product.raw_payload_json, ensure_ascii=False)
    if _has_app_only_marker(payload_text):
        return "raw_payload_json"
    return None


def _has_app_only_marker(value: str) -> bool:
    lowered = value.casefold()
    return any(marker in lowered for marker in MPREIS_APP_ONLY_MARKERS)


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split())
    return cleaned or None


def _is_blank(value: str | None) -> bool:
    return _clean_text(value) is None


def _json_decimal(value: object) -> object:
    if isinstance(value, Decimal):
        return str(value)
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize stored raw products into retailer products for one scrape run."
    )
    parser.add_argument("scrape_run_id", type=int, help="Scrape run containing raw products.")
    parser.add_argument(
        "--retailer",
        choices=["billa", "mpreis"],
        default="billa",
        help="Retailer raw rows to normalize.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help=(
            "For MPREIS, print a non-comparable parser/data-quality report without creating "
            "retailer products."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum missing raw rows to normalize in this run.",
    )
    args = parser.parse_args()
    if args.report_only and args.retailer != "mpreis":
        parser.error("--report-only is only supported for --retailer mpreis")
    if args.retailer == "mpreis" and not args.report_only:
        parser.error("MPREIS normalization is approved only with --report-only")
    return args


if __name__ == "__main__":
    asyncio.run(main())
