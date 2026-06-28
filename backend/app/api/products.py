"""Product search endpoints."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import DEFAULT_SEARCH_LIMIT, search_billa_products
from app.db.session import get_session
from app.models import RetailerProduct

router = APIRouter(prefix="/products", tags=["products"])


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


class ProductSearchResult(BaseModel):
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


class ProductSearchResponse(BaseModel):
    query: str
    retailer: str
    count: int
    items: list[ProductSearchResult]


@router.get("/search", response_model=ProductSearchResponse)
async def search_products(
    q: Annotated[str, Query(min_length=2, description="Search text for BILLA products.")],
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="Maximum number of products to return."),
    ] = DEFAULT_SEARCH_LIMIT,
    session: AsyncSession = Depends(get_session),
) -> ProductSearchResponse:
    query = q.strip()
    if len(query) < 2:
        raise HTTPException(
            status_code=422,
            detail="Search query must contain at least 2 non-space characters.",
        )

    products = await search_billa_products(session, query=query, limit=limit)
    return ProductSearchResponse(
        query=query,
        retailer="billa",
        count=len(products),
        items=[_to_search_result(product) for product in products],
    )


def _to_search_result(product: RetailerProduct) -> ProductSearchResult:
    return ProductSearchResult(
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
    )


def _format_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.normalize(), "f")
