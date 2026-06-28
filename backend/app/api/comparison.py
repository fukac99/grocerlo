"""Canonical product comparison endpoints."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import DEFAULT_SEARCH_LIMIT, search_canonical_product_comparisons
from app.db.comparison import CanonicalProductComparison
from app.db.session import get_session
from app.models import ProductMatch, RetailerProduct

router = APIRouter(tags=["comparison"])


class MoneyResponse(BaseModel):
    amount: str | None
    currency: str | None


class UnitPriceResponse(BaseModel):
    amount: str | None
    unit: str | None
    price_per_base_unit: str | None
    base_unit: str | None


class PackageResponse(BaseModel):
    quantity: str | None
    unit: str | None
    normalized_quantity: str | None
    normalized_unit: str | None


class PromotionResponse(BaseModel):
    is_promotion: bool
    promotion_type: str | None


class MatchResponse(BaseModel):
    match_id: int
    confidence: str
    method: str
    reviewed_status: str


class RetailerOfferResponse(BaseModel):
    id: int
    retailer: str
    country: str
    source_product_id: str | None
    name: str
    brand: str | None
    category: str | None
    price: MoneyResponse
    unit_price: UnitPriceResponse
    package: PackageResponse
    source_url: str | None
    promotion: PromotionResponse
    availability: str | None
    observed_at: datetime
    match: MatchResponse


class CanonicalComparisonResult(BaseModel):
    id: int
    canonical_name: str
    canonical_brand: str | None
    category: str | None
    offer_count: int
    offers: list[RetailerOfferResponse]


class CanonicalComparisonResponse(BaseModel):
    query: str
    count: int
    items: list[CanonicalComparisonResult]


@router.get("/comparison", response_model=CanonicalComparisonResponse)
async def compare_canonical_products(
    query: Annotated[
        str,
        Query(min_length=2, description="Search text for canonical product comparison groups."),
    ],
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Maximum number of canonical groups to return."),
    ] = DEFAULT_SEARCH_LIMIT,
    session: AsyncSession = Depends(get_session),
) -> CanonicalComparisonResponse:
    normalized_query = query.strip()
    if len(normalized_query) < 2:
        raise HTTPException(
            status_code=422,
            detail="Comparison query must contain at least 2 non-space characters.",
        )

    comparisons = await search_canonical_product_comparisons(
        session,
        query=normalized_query,
        limit=limit,
    )
    return CanonicalComparisonResponse(
        query=normalized_query,
        count=len(comparisons),
        items=[_to_comparison_result(comparison) for comparison in comparisons],
    )


def _to_comparison_result(comparison: CanonicalProductComparison) -> CanonicalComparisonResult:
    canonical_product = comparison.canonical_product
    offers = [_to_retailer_offer(match) for match in comparison.offers]
    return CanonicalComparisonResult(
        id=canonical_product.id,
        canonical_name=canonical_product.canonical_name,
        canonical_brand=canonical_product.canonical_brand,
        category=canonical_product.category,
        offer_count=len(offers),
        offers=offers,
    )


def _to_retailer_offer(match: ProductMatch) -> RetailerOfferResponse:
    product: RetailerProduct = match.retailer_product
    return RetailerOfferResponse(
        id=product.id,
        retailer=product.retailer,
        country=product.country,
        source_product_id=product.source_product_id,
        name=product.name,
        brand=product.brand,
        category=product.category,
        price=MoneyResponse(
            amount=_format_decimal(product.price_amount),
            currency=product.currency,
        ),
        unit_price=UnitPriceResponse(
            amount=_format_decimal(product.unit_price_amount),
            unit=product.unit_price_unit,
            price_per_base_unit=_format_decimal(product.price_per_base_unit),
            base_unit=product.normalized_unit_base,
        ),
        package=PackageResponse(
            quantity=_format_decimal(product.package_quantity),
            unit=product.package_unit,
            normalized_quantity=_format_decimal(product.normalized_quantity_base),
            normalized_unit=product.normalized_unit_base,
        ),
        source_url=product.product_url,
        promotion=PromotionResponse(
            is_promotion=product.is_promotion,
            promotion_type=product.promotion_type,
        ),
        availability=product.availability,
        observed_at=product.observed_at,
        match=MatchResponse(
            match_id=match.id,
            confidence=_format_decimal(match.match_confidence) or "0",
            method=match.match_method,
            reviewed_status=match.reviewed_status,
        ),
    )


def _format_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.normalize(), "f")
