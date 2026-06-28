from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.dialects import postgresql

from app.api import comparison as comparison_api
from app.db.comparison import build_canonical_comparison_statement
from app.db.session import get_session
from app.main import app


def test_comparison_returns_canonical_groups_with_retailer_offers(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    async def fake_search_canonical_product_comparisons(session, *, query: str, limit: int):
        captured["session"] = session
        captured["query"] = query
        captured["limit"] = limit
        canonical_product = SimpleNamespace(
            id=10,
            canonical_name="Bio Milch 1 l",
            canonical_brand="Ja! Natürlich",
            category="Milchprodukte",
        )
        billa_offer = SimpleNamespace(
            id=1,
            retailer="billa",
            country="AT",
            source_product_id="produkte/bio-milch",
            product_url="https://shop.billa.at/produkte/bio-milch",
            name="Ja! Natürlich Bio Milch",
            brand="Ja! Natürlich",
            category="Milchprodukte",
            price_amount=Decimal("1.8900"),
            currency="EUR",
            unit_price_amount=Decimal("1.8900"),
            unit_price_unit="1 l",
            package_quantity=Decimal("1.0000"),
            package_unit="l",
            normalized_quantity_base=Decimal("1.0000"),
            normalized_unit_base="l",
            price_per_base_unit=Decimal("1.8900"),
            is_promotion=True,
            promotion_type="discount",
            availability="online",
            observed_at=datetime(2026, 6, 28, 18, 0, tzinfo=UTC),
        )
        mpreis_offer = SimpleNamespace(
            id=2,
            retailer="mpreis",
            country="AT",
            source_product_id="bio-milch-mpreis",
            product_url="https://www.mpreis.at/shop/p/bio-milch-mpreis",
            name="Bio Milch 1L",
            brand=None,
            category="Milchprodukte",
            price_amount=Decimal("1.9900"),
            currency="EUR",
            unit_price_amount=Decimal("1.9900"),
            unit_price_unit="1 l",
            package_quantity=Decimal("1.0000"),
            package_unit="l",
            normalized_quantity_base=Decimal("1.0000"),
            normalized_unit_base="l",
            price_per_base_unit=Decimal("1.9900"),
            is_promotion=False,
            promotion_type=None,
            availability="in_stock",
            observed_at=datetime(2026, 6, 28, 19, 0, tzinfo=UTC),
        )
        return [
            SimpleNamespace(
                canonical_product=canonical_product,
                offers=[
                    SimpleNamespace(
                        id=100,
                        retailer_product=billa_offer,
                        match_confidence=Decimal("0.9300"),
                        match_method="manual_review",
                        reviewed_status="manual",
                    ),
                    SimpleNamespace(
                        id=101,
                        retailer_product=mpreis_offer,
                        match_confidence=Decimal("0.8800"),
                        match_method="rule_based_v1",
                        reviewed_status="accepted",
                    ),
                ],
            )
        ]

    async def fake_session():
        yield "fake-session"

    monkeypatch.setattr(
        comparison_api,
        "search_canonical_product_comparisons",
        fake_search_canonical_product_comparisons,
    )
    app.dependency_overrides[get_session] = fake_session

    try:
        response = TestClient(app).get("/comparison", params={"query": "  Bio Milch  ", "limit": 5})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert captured == {"session": "fake-session", "query": "Bio Milch", "limit": 5}
    assert response.json() == {
        "query": "Bio Milch",
        "count": 1,
        "items": [
            {
                "id": 10,
                "canonical_name": "Bio Milch 1 l",
                "canonical_brand": "Ja! Natürlich",
                "category": "Milchprodukte",
                "offer_count": 2,
                "offers": [
                    {
                        "id": 1,
                        "retailer": "billa",
                        "country": "AT",
                        "source_product_id": "produkte/bio-milch",
                        "name": "Ja! Natürlich Bio Milch",
                        "brand": "Ja! Natürlich",
                        "category": "Milchprodukte",
                        "price": {"amount": "1.89", "currency": "EUR"},
                        "unit_price": {
                            "amount": "1.89",
                            "unit": "1 l",
                            "price_per_base_unit": "1.89",
                            "base_unit": "l",
                        },
                        "package": {
                            "quantity": "1",
                            "unit": "l",
                            "normalized_quantity": "1",
                            "normalized_unit": "l",
                        },
                        "source_url": "https://shop.billa.at/produkte/bio-milch",
                        "promotion": {"is_promotion": True, "promotion_type": "discount"},
                        "availability": "online",
                        "observed_at": "2026-06-28T18:00:00Z",
                        "match": {
                            "match_id": 100,
                            "confidence": "0.93",
                            "method": "manual_review",
                            "reviewed_status": "manual",
                        },
                    },
                    {
                        "id": 2,
                        "retailer": "mpreis",
                        "country": "AT",
                        "source_product_id": "bio-milch-mpreis",
                        "name": "Bio Milch 1L",
                        "brand": None,
                        "category": "Milchprodukte",
                        "price": {"amount": "1.99", "currency": "EUR"},
                        "unit_price": {
                            "amount": "1.99",
                            "unit": "1 l",
                            "price_per_base_unit": "1.99",
                            "base_unit": "l",
                        },
                        "package": {
                            "quantity": "1",
                            "unit": "l",
                            "normalized_quantity": "1",
                            "normalized_unit": "l",
                        },
                        "source_url": "https://www.mpreis.at/shop/p/bio-milch-mpreis",
                        "promotion": {"is_promotion": False, "promotion_type": None},
                        "availability": "in_stock",
                        "observed_at": "2026-06-28T19:00:00Z",
                        "match": {
                            "match_id": 101,
                            "confidence": "0.88",
                            "method": "rule_based_v1",
                            "reviewed_status": "accepted",
                        },
                    },
                ],
            }
        ],
    }


def test_comparison_validates_query_length() -> None:
    client = TestClient(app)

    assert client.get("/comparison", params={"query": "m"}).status_code == 422
    assert client.get("/comparison", params={"query": "   "}).status_code == 422


def test_canonical_comparison_statement_matches_terms_and_reviewed_matches() -> None:
    statement = build_canonical_comparison_statement("Bio 50%_Milch", limit=5)

    compiled = str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )

    assert "canonical_products" in compiled
    assert "product_matches.reviewed_status IN ('accepted', 'manual')" in compiled
    assert compiled.count("ILIKE") == 12
    assert "canonical_products.canonical_name" in compiled
    assert "canonical_products.canonical_brand" in compiled
    assert "retailer_products.name" in compiled
    assert "retailer_products.brand" in compiled
    assert "retailer_products.retailer = 'billa'" not in compiled
    assert "LIMIT 5" in compiled
    assert "50\\\\%%\\\\_milch" in compiled
