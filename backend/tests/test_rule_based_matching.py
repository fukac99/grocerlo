from dataclasses import dataclass
from decimal import Decimal

from app.matching import (
    CANDIDATE_THRESHOLD,
    STRONG_MATCH_THRESHOLD,
    rank_product_candidates,
    score_product_candidate,
)


@dataclass(frozen=True)
class ProductFixture:
    name: str
    brand: str | None
    category: str | None
    normalized_quantity_base: Decimal | None
    normalized_unit_base: str | None


def product(
    *,
    name: str = "Ritter Sport Voll-Nuss Schokolade 100 g",
    brand: str | None = "Ritter Sport",
    category: str | None = "Süßwaren Schokolade",
    quantity: Decimal | None = Decimal("0.1000"),
    unit: str | None = "kg",
) -> ProductFixture:
    return ProductFixture(
        name=name,
        brand=brand,
        category=category,
        normalized_quantity_base=quantity,
        normalized_unit_base=unit,
    )


def component_scores(score) -> dict[str, Decimal]:
    return {component.name: component.score for component in score.components}


def test_rule_based_matching_scores_strong_brand_name_package_match() -> None:
    billa_product = product()
    mpreis_product = product(name="Ritter Sport Alpenvollmilch Voll-Nuss Schokolade 100g")

    score = score_product_candidate(billa_product, mpreis_product)

    assert score.score >= STRONG_MATCH_THRESHOLD
    assert score.is_candidate is True
    assert score.is_strong_match is True
    assert score.blockers == ()
    assert component_scores(score)["brand"] == Decimal("1")
    assert component_scores(score)["package"] == Decimal("1")
    explanation = score.explain()
    assert explanation["threshold"] == str(CANDIDATE_THRESHOLD)
    assert explanation["strong_threshold"] == str(STRONG_MATCH_THRESHOLD)
    assert {component["name"] for component in explanation["components"]} == {
        "brand",
        "normalized_name",
        "package",
        "category",
        "unit",
    }


def test_rule_based_matching_rejects_incompatible_package_size() -> None:
    billa_product = product(quantity=Decimal("0.1000"))
    mpreis_product = product(quantity=Decimal("0.2500"))

    score = score_product_candidate(billa_product, mpreis_product)

    assert score.score < CANDIDATE_THRESHOLD
    assert score.is_candidate is False
    assert "package_mismatch" in score.blockers
    assert component_scores(score)["package"] == Decimal("0")


def test_rule_based_matching_rejects_incompatible_category() -> None:
    billa_product = product(category="Milchprodukte")
    mpreis_product = product(category="Tiernahrung")

    score = score_product_candidate(billa_product, mpreis_product)

    assert score.score < CANDIDATE_THRESHOLD
    assert score.is_candidate is False
    assert "category_mismatch" in score.blockers
    assert component_scores(score)["category"] == Decimal("0.0000")


def test_rule_based_matching_rejects_incompatible_unit() -> None:
    billa_product = product(name="Ja! Natürlich Milch 1 l", category="Milchprodukte", unit="l")
    mpreis_product = product(name="Ja! Natürlich Milch 1 kg", category="Milchprodukte", unit="kg")

    score = score_product_candidate(billa_product, mpreis_product)

    assert score.score < CANDIDATE_THRESHOLD
    assert score.is_candidate is False
    assert "unit_mismatch" in score.blockers
    assert component_scores(score)["unit"] == Decimal("0")


def test_rule_based_matching_rejects_generic_unbranded_false_positive() -> None:
    billa_product = product(
        name="Milch 1 l",
        brand=None,
        category="Milchprodukte",
        quantity=Decimal("1.0000"),
        unit="l",
    )
    mpreis_product = product(
        name="Frische Milch 1 l",
        brand=None,
        category="Milchprodukte",
        quantity=Decimal("1.0000"),
        unit="l",
    )

    score = score_product_candidate(billa_product, mpreis_product)

    assert score.score < CANDIDATE_THRESHOLD
    assert score.is_candidate is False
    assert "generic_name_without_brand" in score.blockers


def test_rule_based_matching_rejects_private_label_generic_name_false_positive() -> None:
    billa_product = product(
        name="Clever Vollmilch 1 l",
        brand="Clever",
        category="Milchprodukte",
        quantity=Decimal("1.0000"),
        unit="l",
    )
    mpreis_product = product(
        name="Milsani Vollmilch 1 l",
        brand="Milsani",
        category="Milchprodukte",
        quantity=Decimal("1.0000"),
        unit="l",
    )

    score = score_product_candidate(billa_product, mpreis_product)

    assert score.score < CANDIDATE_THRESHOLD
    assert score.is_candidate is False
    assert "generic_name_brand_mismatch" in score.blockers


def test_rule_based_matching_ranks_only_threshold_passing_candidates() -> None:
    billa_product = product()
    candidates = [
        product(name="Milch 1 l", brand=None, category="Milchprodukte", quantity=Decimal("1.0")),
        product(name="Ritter Sport Alpenvollmilch Voll-Nuss Schokolade 100g"),
    ]

    ranked = rank_product_candidates(billa_product, candidates)

    assert [match.candidate.name for match in ranked] == [
        "Ritter Sport Alpenvollmilch Voll-Nuss Schokolade 100g"
    ]
