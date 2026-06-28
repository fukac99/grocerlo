#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.db import normalize_retailer_products_for_scrape_run  # noqa: E402
from app.db.session import async_session_factory  # noqa: E402


async def main() -> None:
    args = parse_args()
    async with async_session_factory() as session:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize stored raw products into retailer products for one scrape run."
    )
    parser.add_argument("scrape_run_id", type=int, help="Scrape run containing raw products.")
    parser.add_argument(
        "--retailer",
        choices=["billa"],
        default="billa",
        help="Retailer raw rows to normalize.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum missing raw rows to normalize in this run.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main())
