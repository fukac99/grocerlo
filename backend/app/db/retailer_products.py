"""Database helpers for retailer product normalization."""

from dataclasses import dataclass, field

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RawProduct, RetailerProduct, ScrapeRun
from app.normalization import (
    RawProductNormalizationError,
    normalize_raw_product_to_retailer_product,
)


@dataclass(frozen=True)
class SkippedRawProduct:
    raw_product_id: int
    reason: str


@dataclass(frozen=True)
class RetailerProductNormalizationResult:
    scrape_run_id: int
    retailer: str
    existing: int
    created: int
    skipped: list[SkippedRawProduct] = field(default_factory=list)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)


async def normalize_retailer_products_for_scrape_run(
    session: AsyncSession,
    *,
    scrape_run_id: int,
    retailer: str = "billa",
    limit: int | None = None,
) -> RetailerProductNormalizationResult:
    """Create missing retailer products for one scrape run without touching raw rows."""
    scrape_run = await session.get(ScrapeRun, scrape_run_id)
    if scrape_run is None:
        raise ValueError(f"scrape_run_id does not exist: {scrape_run_id}")

    existing = await _count_existing(session, scrape_run_id=scrape_run_id, retailer=retailer)
    raw_products = await _select_unmatched_raw_products(
        session,
        scrape_run_id=scrape_run_id,
        retailer=retailer,
        limit=limit,
    )

    created = 0
    skipped: list[SkippedRawProduct] = []
    for raw_product in raw_products:
        try:
            fields = normalize_raw_product_to_retailer_product(raw_product)
        except RawProductNormalizationError as exc:
            skipped.append(SkippedRawProduct(raw_product_id=raw_product.id, reason=str(exc)))
            continue

        session.add(RetailerProduct(**fields.as_model_kwargs()))
        created += 1

    await session.flush()
    return RetailerProductNormalizationResult(
        scrape_run_id=scrape_run_id,
        retailer=retailer,
        existing=existing,
        created=created,
        skipped=skipped,
    )


async def _count_existing(
    session: AsyncSession,
    *,
    scrape_run_id: int,
    retailer: str,
) -> int:
    result = await session.execute(
        select(func.count())
        .select_from(RawProduct)
        .join(RetailerProduct, RetailerProduct.raw_product_id == RawProduct.id)
        .where(RawProduct.scrape_run_id == scrape_run_id, RawProduct.retailer == retailer)
    )
    return int(result.scalar_one())


async def _select_unmatched_raw_products(
    session: AsyncSession,
    *,
    scrape_run_id: int,
    retailer: str,
    limit: int | None,
) -> list[RawProduct]:
    statement = (
        select(RawProduct)
        .outerjoin(RetailerProduct, RetailerProduct.raw_product_id == RawProduct.id)
        .where(
            RawProduct.scrape_run_id == scrape_run_id,
            RawProduct.retailer == retailer,
            RetailerProduct.id.is_(None),
        )
        .order_by(RawProduct.id)
    )
    if limit is not None:
        statement = statement.limit(limit)

    result = await session.execute(statement)
    return list(result.scalars().all())


__all__ = [
    "RetailerProductNormalizationResult",
    "SkippedRawProduct",
    "normalize_retailer_products_for_scrape_run",
]
