"""Comparison helpers for canonical products and matched retailer offers."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Select, and_, false, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.product_search import DEFAULT_SEARCH_LIMIT, MAX_SEARCH_LIMIT, normalize_product_search_terms
from app.models import CanonicalProduct, ProductMatch, RetailerProduct
from app.models.scraping import ProductMatchReviewStatus

COMPARISON_MATCH_STATUSES = (
    ProductMatchReviewStatus.ACCEPTED.value,
    ProductMatchReviewStatus.MANUAL.value,
)

_LIKE_ESCAPE_CHARS = str.maketrans(
    {
        "\\": "\\\\",
        "%": "\\%",
        "_": "\\_",
    }
)


@dataclass(frozen=True)
class CanonicalProductComparison:
    canonical_product: CanonicalProduct
    offers: list[ProductMatch]


def build_canonical_comparison_statement(
    query: str,
    *,
    limit: int = DEFAULT_SEARCH_LIMIT,
) -> Select[tuple[CanonicalProduct]]:
    """Build a conservative canonical-product comparison search statement.

    Query terms are matched literally across canonical fields and matched retailer
    product fields. Only reviewed accepted/manual matches are eligible for
    comparison results; rejected and unreviewed candidates stay out of this API.
    """
    terms = normalize_product_search_terms(query)
    clamped_limit = max(1, min(limit, MAX_SEARCH_LIMIT))
    filters = [_term_filter(term) for term in terms] if terms else [false()]

    return (
        select(CanonicalProduct)
        .join(ProductMatch)
        .join(RetailerProduct)
        .options(
            selectinload(CanonicalProduct.product_matches).selectinload(
                ProductMatch.retailer_product
            )
        )
        .where(ProductMatch.reviewed_status.in_(COMPARISON_MATCH_STATUSES), and_(*filters))
        .distinct()
        .order_by(CanonicalProduct.canonical_name, CanonicalProduct.id)
        .limit(clamped_limit)
    )


async def search_canonical_product_comparisons(
    session: AsyncSession,
    *,
    query: str,
    limit: int = DEFAULT_SEARCH_LIMIT,
) -> list[CanonicalProductComparison]:
    statement = build_canonical_comparison_statement(query, limit=limit)
    result = await session.execute(statement)
    canonical_products = list(result.scalars().unique().all())

    return [
        CanonicalProductComparison(
            canonical_product=canonical_product,
            offers=_comparison_offers(canonical_product.product_matches),
        )
        for canonical_product in canonical_products
    ]


def _comparison_offers(matches: list[ProductMatch]) -> list[ProductMatch]:
    eligible_matches = [
        match
        for match in matches
        if match.reviewed_status in COMPARISON_MATCH_STATUSES and match.retailer_product is not None
    ]
    return sorted(
        eligible_matches,
        key=lambda match: (
            match.retailer_product.retailer,
            match.retailer_product.country,
            match.retailer_product.name,
            match.retailer_product.id,
        ),
    )


def _term_filter(term: str):
    pattern = f"%{_escape_like(term)}%"
    return or_(
        CanonicalProduct.canonical_name.ilike(pattern, escape="\\"),
        CanonicalProduct.canonical_brand.ilike(pattern, escape="\\"),
        CanonicalProduct.category.ilike(pattern, escape="\\"),
        RetailerProduct.name.ilike(pattern, escape="\\"),
        RetailerProduct.brand.ilike(pattern, escape="\\"),
        RetailerProduct.category.ilike(pattern, escape="\\"),
    )


def _escape_like(value: str) -> str:
    return value.translate(_LIKE_ESCAPE_CHARS)


__all__ = [
    "COMPARISON_MATCH_STATUSES",
    "CanonicalProductComparison",
    "build_canonical_comparison_statement",
    "search_canonical_product_comparisons",
]
