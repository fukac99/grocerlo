"""Search helpers for normalized retailer products."""

from __future__ import annotations

import re

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RetailerProduct

BILLA_RETAILER = "billa"
DEFAULT_SEARCH_LIMIT = 25
MAX_SEARCH_LIMIT = 100

_SEARCH_TERM_RE = re.compile(r"\S+")
_LIKE_ESCAPE_CHARS = str.maketrans(
    {
        "\\": "\\\\",
        "%": "\\%",
        "_": "\\_",
    }
)


def normalize_product_search_terms(query: str) -> list[str]:
    """Normalize user search text into simple terms matched across product fields."""
    return [match.group(0).casefold() for match in _SEARCH_TERM_RE.finditer(query.strip())]


def build_billa_product_search_statement(
    query: str,
    *,
    limit: int = DEFAULT_SEARCH_LIMIT,
) -> Select[tuple[RetailerProduct]]:
    """Build a BILLA-only product search statement.

    All query terms must match at least one of name, brand, or category. Terms are
    matched case-insensitively and literally, so SQL wildcard characters in user
    input do not broaden the search.
    """
    terms = normalize_product_search_terms(query)
    clamped_limit = max(1, min(limit, MAX_SEARCH_LIMIT))

    filters = [RetailerProduct.retailer == BILLA_RETAILER]
    filters.extend(_term_filter(term) for term in terms)

    return (
        select(RetailerProduct)
        .where(and_(*filters))
        .order_by(RetailerProduct.name, RetailerProduct.id)
        .limit(clamped_limit)
    )


async def search_billa_products(
    session: AsyncSession,
    *,
    query: str,
    limit: int = DEFAULT_SEARCH_LIMIT,
) -> list[RetailerProduct]:
    statement = build_billa_product_search_statement(query, limit=limit)
    result = await session.execute(statement)
    return list(result.scalars().all())


def _term_filter(term: str):
    pattern = f"%{_escape_like(term)}%"
    return or_(
        RetailerProduct.name.ilike(pattern, escape="\\"),
        RetailerProduct.brand.ilike(pattern, escape="\\"),
        RetailerProduct.category.ilike(pattern, escape="\\"),
    )


def _escape_like(value: str) -> str:
    return value.translate(_LIKE_ESCAPE_CHARS)


__all__ = [
    "BILLA_RETAILER",
    "DEFAULT_SEARCH_LIMIT",
    "MAX_SEARCH_LIMIT",
    "build_billa_product_search_statement",
    "normalize_product_search_terms",
    "search_billa_products",
]
