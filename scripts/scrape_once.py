#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.scrapers import (  # noqa: E402
    BillaScraper,
    MpreisScraper,
    RawProductPayload,
    RetailerScraper,
    ReweScraper,
    ScraperStopCondition,
)


async def main() -> None:
    args = parse_args()
    validate_positive_limit("--limit-categories", args.limit_categories)
    validate_positive_limit("--max-products", args.max_products)
    validate_storage_policy(args)

    scraper = build_scraper(args)

    categories = await scraper.scrape_categories()
    categories = categories[: args.limit_categories]

    products: list[RawProductPayload] = []
    for category in categories:
        try:
            category_products = await scraper.scrape_products(category)
        except ScraperStopCondition as exc:
            raise SystemExit(str(exc)) from exc
        remaining = args.max_products - len(products)
        products.extend(category_products[:remaining])
        if len(products) >= args.max_products:
            break

    if args.store:
        scrape_run_id = await store_raw_products(
            retailer=scraper.retailer,
            country=scraper.country,
            source_url=scraper.category_url,
            products=products,
        )
        print(json.dumps({"scrape_run_id": scrape_run_id, "raw_products": len(products)}, indent=2))
        return

    print(
        json.dumps(
            {
                "retailer": scraper.retailer,
                "country": scraper.country,
                "categories": [asdict(category) for category in categories],
                "products": [asdict(product) for product in products],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one low-volume grocery scraper.")
    parser.add_argument(
        "--retailer",
        choices=["billa", "mpreis", "rewe"],
        default="billa",
        help="Retailer scraper to run.",
    )
    parser.add_argument(
        "--limit-categories",
        type=int,
        default=1,
        help="Maximum categories to scrape during this one-off run.",
    )
    parser.add_argument(
        "--max-products",
        type=int,
        default=10,
        help="Maximum total products to extract.",
    )
    parser.add_argument(
        "--store",
        action="store_true",
        help="Store raw products in Postgres. Omit for JSON dry-run output.",
    )
    return parser.parse_args()


def validate_positive_limit(name: str, value: int) -> None:
    if value < 1:
        raise SystemExit(f"{name} must be at least 1.")


def validate_storage_policy(args: argparse.Namespace) -> None:
    if args.store and args.retailer == "rewe":
        raise SystemExit("REWE is approved for no-storage dry runs only.")

    if not args.store or args.retailer != "mpreis":
        return

    if args.limit_categories != 1:
        raise SystemExit("MPREIS stored validation is capped at exactly 1 category-equivalent page.")
    if args.max_products > 3:
        raise SystemExit("MPREIS stored validation is capped at 3 raw products.")


def build_scraper(args: argparse.Namespace) -> RetailerScraper:
    if args.retailer == "billa":
        return BillaScraper(max_products_per_category=args.max_products)
    if args.retailer == "mpreis":
        return MpreisScraper(max_products_per_category=min(args.max_products, 3))
    if args.retailer == "rewe":
        return ReweScraper(max_products_per_category=min(args.max_products, 3))
    raise ValueError(f"Unsupported retailer: {args.retailer}")


async def store_raw_products(
    *,
    retailer: str,
    country: str,
    source_url: str,
    products: list[RawProductPayload],
) -> int:
    from app.db.session import async_session_factory
    from app.models.scraping import RawProduct, ScrapeRun, ScrapeRunStatus

    async with async_session_factory() as session:
        scrape_run = ScrapeRun(
            retailer=retailer,
            country=country,
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

        scrape_run.status = ScrapeRunStatus.SUCCEEDED.value
        scrape_run.finished_at = datetime.now(UTC)
        await session.commit()
        return scrape_run.id


if __name__ == "__main__":
    asyncio.run(main())
