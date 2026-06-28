"""Deterministic product candidate scoring for cross-retailer matching."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from difflib import SequenceMatcher
import re
import unicodedata
from typing import Protocol


RULE_BASED_MATCH_METHOD = "rule_based_v1"
CANDIDATE_THRESHOLD = Decimal("0.65")
STRONG_MATCH_THRESHOLD = Decimal("0.82")


class ProductLike(Protocol):
    name: str
    brand: str | None
    category: str | None
    normalized_quantity_base: Decimal | None
    normalized_unit_base: str | None


@dataclass(frozen=True)
class ScoreComponent:
    name: str
    score: Decimal
    weight: Decimal
    reason: str

    @property
    def contribution(self) -> Decimal:
        return self.score * self.weight


@dataclass(frozen=True)
class ProductMatchScore:
    source: ProductLike
    candidate: ProductLike
    score: Decimal
    is_candidate: bool
    is_strong_match: bool
    threshold: Decimal
    strong_threshold: Decimal
    method: str
    components: tuple[ScoreComponent, ...]
    blockers: tuple[str, ...] = ()

    def explain(self) -> dict[str, object]:
        return {
            "method": self.method,
            "score": str(self.score),
            "is_candidate": self.is_candidate,
            "is_strong_match": self.is_strong_match,
            "threshold": str(self.threshold),
            "strong_threshold": str(self.strong_threshold),
            "components": [
                {
                    "name": component.name,
                    "score": str(component.score),
                    "weight": str(component.weight),
                    "contribution": str(component.contribution),
                    "reason": component.reason,
                }
                for component in self.components
            ],
            "blockers": list(self.blockers),
        }


_WEIGHTS = {
    "brand": Decimal("0.25"),
    "normalized_name": Decimal("0.35"),
    "package": Decimal("0.20"),
    "category": Decimal("0.10"),
    "unit": Decimal("0.10"),
}
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "bio",
    "der",
    "die",
    "das",
    "ein",
    "eine",
    "extra",
    "frisch",
    "fresh",
    "natur",
    "original",
    "premium",
    "und",
    "von",
}
_PACKAGE_TOKENS = {
    "g",
    "gramm",
    "kg",
    "kilogramm",
    "l",
    "liter",
    "lt",
    "ml",
    "stk",
    "stueck",
    "stuck",
    "piece",
    "pieces",
}


def score_product_candidate(
    source: ProductLike,
    candidate: ProductLike,
    *,
    threshold: Decimal = CANDIDATE_THRESHOLD,
    strong_threshold: Decimal = STRONG_MATCH_THRESHOLD,
) -> ProductMatchScore:
    """Score a cross-retailer product candidate with explainable components."""

    components = (
        _score_brand(source.brand, candidate.brand),
        _score_normalized_name(source, candidate),
        _score_package(source, candidate),
        _score_category(source.category, candidate.category),
        _score_unit(source.normalized_unit_base, candidate.normalized_unit_base),
    )
    blockers = _blockers(source, candidate)
    raw_score = sum((component.contribution for component in components), Decimal("0"))
    score = min(raw_score, Decimal("0.64")) if blockers else raw_score
    score = score.quantize(Decimal("0.0001"))

    return ProductMatchScore(
        source=source,
        candidate=candidate,
        score=score,
        is_candidate=score >= threshold and not blockers,
        is_strong_match=score >= strong_threshold and not blockers,
        threshold=threshold,
        strong_threshold=strong_threshold,
        method=RULE_BASED_MATCH_METHOD,
        components=components,
        blockers=blockers,
    )


def rank_product_candidates(
    source: ProductLike,
    candidates: list[ProductLike],
    *,
    threshold: Decimal = CANDIDATE_THRESHOLD,
    strong_threshold: Decimal = STRONG_MATCH_THRESHOLD,
) -> list[ProductMatchScore]:
    """Return threshold-passing candidates sorted by highest deterministic score."""

    scored = [
        score_product_candidate(
            source,
            candidate,
            threshold=threshold,
            strong_threshold=strong_threshold,
        )
        for candidate in candidates
    ]
    return sorted(
        (score for score in scored if score.is_candidate),
        key=lambda score: (-score.score, _normalize_text(score.candidate.name)),
    )


def _score_brand(source_brand: str | None, candidate_brand: str | None) -> ScoreComponent:
    source = _normalize_text(source_brand)
    candidate = _normalize_text(candidate_brand)
    if source and candidate and source == candidate:
        return ScoreComponent("brand", Decimal("1"), _WEIGHTS["brand"], "brands match exactly")
    if source and candidate:
        return ScoreComponent("brand", Decimal("0"), _WEIGHTS["brand"], "brands differ")
    if not source and not candidate:
        return ScoreComponent("brand", Decimal("0.35"), _WEIGHTS["brand"], "both brands missing")
    return ScoreComponent("brand", Decimal("0.20"), _WEIGHTS["brand"], "one brand missing")


def _score_normalized_name(source: ProductLike, candidate: ProductLike) -> ScoreComponent:
    source_name = _normalized_name_for_similarity(source)
    candidate_name = _normalized_name_for_similarity(candidate)
    if not source_name or not candidate_name:
        return ScoreComponent(
            "normalized_name",
            Decimal("0"),
            _WEIGHTS["normalized_name"],
            "missing normalized name tokens",
        )

    ratio = SequenceMatcher(None, source_name, candidate_name).ratio()
    token_score = _token_overlap_score(_tokens(source_name), _tokens(candidate_name))
    score = Decimal(str((ratio * 0.60) + (token_score * 0.40))).quantize(Decimal("0.0001"))
    return ScoreComponent(
        "normalized_name",
        score,
        _WEIGHTS["normalized_name"],
        f"name similarity ratio={ratio:.2f}, token_overlap={token_score:.2f}",
    )


def _score_package(source: ProductLike, candidate: ProductLike) -> ScoreComponent:
    source_unit = _normalize_text(source.normalized_unit_base)
    candidate_unit = _normalize_text(candidate.normalized_unit_base)
    source_quantity = source.normalized_quantity_base
    candidate_quantity = candidate.normalized_quantity_base
    if source_quantity is None or candidate_quantity is None:
        return ScoreComponent("package", Decimal("0.50"), _WEIGHTS["package"], "package missing")
    if not source_unit or not candidate_unit:
        return ScoreComponent("package", Decimal("0.50"), _WEIGHTS["package"], "unit missing")
    if source_unit != candidate_unit:
        return ScoreComponent(
            "package",
            Decimal("0"),
            _WEIGHTS["package"],
            f"package units differ: {source_unit} vs {candidate_unit}",
        )
    if source_quantity == 0 or candidate_quantity == 0:
        return ScoreComponent("package", Decimal("0"), _WEIGHTS["package"], "zero package size")

    larger = max(source_quantity, candidate_quantity)
    smaller = min(source_quantity, candidate_quantity)
    difference = (larger - smaller) / larger
    if difference <= Decimal("0.02"):
        score = Decimal("1")
    elif difference <= Decimal("0.10"):
        score = Decimal("0.75")
    elif difference <= Decimal("0.25"):
        score = Decimal("0.25")
    else:
        score = Decimal("0")
    return ScoreComponent(
        "package",
        score,
        _WEIGHTS["package"],
        f"normalized package difference={difference:.2%}",
    )


def _score_category(source_category: str | None, candidate_category: str | None) -> ScoreComponent:
    source_tokens = set(_tokens(_normalize_text(source_category)))
    candidate_tokens = set(_tokens(_normalize_text(candidate_category)))
    if not source_tokens or not candidate_tokens:
        return ScoreComponent("category", Decimal("0.50"), _WEIGHTS["category"], "category missing")
    if source_tokens == candidate_tokens:
        return ScoreComponent("category", Decimal("1"), _WEIGHTS["category"], "categories match")

    overlap = _token_overlap_score(tuple(source_tokens), tuple(candidate_tokens))
    score = Decimal(str(overlap)).quantize(Decimal("0.0001"))
    return ScoreComponent(
        "category",
        score,
        _WEIGHTS["category"],
        f"category token overlap={overlap:.2f}",
    )


def _score_unit(source_unit: str | None, candidate_unit: str | None) -> ScoreComponent:
    source = _normalize_text(source_unit)
    candidate = _normalize_text(candidate_unit)
    if source and candidate and source == candidate:
        return ScoreComponent("unit", Decimal("1"), _WEIGHTS["unit"], "base units match")
    if source and candidate:
        return ScoreComponent("unit", Decimal("0"), _WEIGHTS["unit"], "base units differ")
    return ScoreComponent("unit", Decimal("0.50"), _WEIGHTS["unit"], "unit missing")


def _blockers(source: ProductLike, candidate: ProductLike) -> tuple[str, ...]:
    blockers: list[str] = []
    source_unit = _normalize_text(source.normalized_unit_base)
    candidate_unit = _normalize_text(candidate.normalized_unit_base)
    if source_unit and candidate_unit and source_unit != candidate_unit:
        blockers.append("unit_mismatch")

    source_quantity = source.normalized_quantity_base
    candidate_quantity = candidate.normalized_quantity_base
    if (
        source_quantity is not None
        and candidate_quantity is not None
        and source_unit
        and candidate_unit
        and source_unit == candidate_unit
        and _quantity_difference(source_quantity, candidate_quantity) > Decimal("0.25")
    ):
        blockers.append("package_mismatch")

    source_category_tokens = set(_tokens(_normalize_text(source.category)))
    candidate_category_tokens = set(_tokens(_normalize_text(candidate.category)))
    if source_category_tokens and candidate_category_tokens and not (
        source_category_tokens & candidate_category_tokens
    ):
        blockers.append("category_mismatch")

    source_brand = _normalize_text(source.brand)
    candidate_brand = _normalize_text(candidate.brand)
    source_core_tokens = _core_name_tokens(source)
    candidate_core_tokens = _core_name_tokens(candidate)
    if len(source_core_tokens | candidate_core_tokens) <= 2:
        if not source_brand and not candidate_brand:
            blockers.append("generic_name_without_brand")
        elif source_brand and candidate_brand and source_brand != candidate_brand:
            blockers.append("generic_name_brand_mismatch")

    return tuple(blockers)


def _quantity_difference(source_quantity: Decimal, candidate_quantity: Decimal) -> Decimal:
    if source_quantity == 0 or candidate_quantity == 0:
        return Decimal("1")
    larger = max(source_quantity, candidate_quantity)
    smaller = min(source_quantity, candidate_quantity)
    return (larger - smaller) / larger


def _normalized_name_for_similarity(product: ProductLike) -> str:
    brand_tokens = set(_tokens(_normalize_text(product.brand)))
    tokens = [
        token
        for token in _tokens(_normalize_text(product.name))
        if token not in brand_tokens and token not in _PACKAGE_TOKENS and not token.isdigit()
    ]
    return " ".join(tokens)


def _core_name_tokens(product: ProductLike) -> set[str]:
    return {
        token
        for token in _tokens(_normalized_name_for_similarity(product))
        if token not in _STOPWORDS and not token.isdigit()
    }


def _token_overlap_score(source_tokens: tuple[str, ...], candidate_tokens: tuple[str, ...]) -> float:
    source = set(source_tokens)
    candidate = set(candidate_tokens)
    if not source or not candidate:
        return 0.0
    return len(source & candidate) / len(source | candidate)


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(_TOKEN_RE.findall(value))


def _normalize_text(value: object | None) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value).casefold())
    text = "".join(character for character in text if not unicodedata.combining(character))
    return " ".join(_TOKEN_RE.findall(text))
