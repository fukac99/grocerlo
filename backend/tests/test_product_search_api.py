from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql

from app.api import products as products_api
from app.db.product_search import (
    build_billa_product_search_statement,
    normalize_product_search_terms,
)
from app.db.session import get_session
from app.main import app


def test_search_products_returns_normalized_billa_products(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    async def fake_search_billa_products(session, *, query: str, limit: int):
        captured["session"] = session
        captured["query"] = query
        captured["limit"] = limit
        return [
            SimpleNamespace(
                id=1,
                retailer="billa",
                country="AT",
                source_product_id="produkte/billa-bio-milch",
                product_url="https://shop.billa.at/produkte/billa-bio-milch",
                name="BILLA Bio Milch",
                brand="BILLA Bio",
                category="Milchprodukte",
                price_amount=Decimal("2.3900"),
                currency="EUR",
                unit_price_amount=Decimal("2.3900"),
                unit_price_unit="1 l",
                package_quantity=Decimal("1.0000"),
                package_unit="l",
                normalized_quantity_base=Decimal("1.0000"),
                normalized_unit_base="l",
                price_per_base_unit=Decimal("2.3900"),
                is_promotion=True,
                promotion_type="discount",
                availability="online",
                observed_at=datetime(2026, 6, 28, 18, 0, tzinfo=UTC),
            )
        ]

    async def fake_session():
        yield "fake-session"

    monkeypatch.setattr(products_api, "search_billa_products", fake_search_billa_products)
    app.dependency_overrides[get_session] = fake_session

    try:
        response = TestClient(app).get("/products/search", params={"q": "  Bio Milch  ", "limit": 5})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert captured == {"session": "fake-session", "query": "Bio Milch", "limit": 5}
    assert response.json() == {
        "query": "Bio Milch",
        "retailer": "billa",
        "count": 1,
        "items": [
            {
                "id": 1,
                "retailer": "billa",
                "country": "AT",
                "source_product_id": "produkte/billa-bio-milch",
                "name": "BILLA Bio Milch",
                "brand": "BILLA Bio",
                "category": "Milchprodukte",
                "price": {"amount": "2.39", "currency": "EUR"},
                "unit_price": {
                    "amount": "2.39",
                    "unit": "1 l",
                    "price_per_base_unit": "2.39",
                    "base_unit": "l",
                },
                "package": {
                    "quantity": "1",
                    "unit": "l",
                    "normalized_quantity": "1",
                    "normalized_unit": "l",
                },
                "source_url": "https://shop.billa.at/produkte/billa-bio-milch",
                "promotion": {"is_promotion": True, "promotion_type": "discount"},
                "availability": "online",
                "observed_at": "2026-06-28T18:00:00Z",
            }
        ],
    }


def test_search_products_validates_query_length() -> None:
    client = TestClient(app)

    assert client.get("/products/search", params={"q": "m"}).status_code == 422
    assert client.get("/products/search", params={"q": "   "}).status_code == 422


def test_normalize_product_search_terms_splits_casefolded_terms() -> None:
    assert normalize_product_search_terms("  BILLA   Bio Milch  ") == ["billa", "bio", "milch"]


def test_billa_product_search_statement_matches_terms_across_normalized_fields() -> None:
    statement = build_billa_product_search_statement("Bio 50%_Milch", limit=5)

    compiled = str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )

    assert "retailer_products.retailer = 'billa'" in compiled
    assert compiled.count("ILIKE") == 6
    assert "retailer_products.name" in compiled
    assert "retailer_products.brand" in compiled
    assert "retailer_products.category" in compiled
    assert "LIMIT 5" in compiled
    assert "50\\\\%%\\\\_milch" in compiled
