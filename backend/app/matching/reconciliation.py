"""Read-only reconciliation reporting for normalized retailer products."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable

from app.matching.rule_based import (
    CANDIDATE_THRESHOLD,
    RULE_BASED_MATCH_METHOD,
    STRONG_MATCH_THRESHOLD,
    ProductMatchScore,
    score_product_candidate,
)

REVIEW_THRESHOLD = Decimal("0.50")


@dataclass(frozen=True)
class ReconciliationOptions:
    candidate_threshold: Decimal = CANDIDATE_THRESHOLD
    strong_threshold: Decimal = STRONG_MATCH_THRESHOLD
    review_threshold: Decimal = REVIEW_THRESHOLD
    max_examples: int = 20


def build_reconciliation_report(
    products: Iterable[Any],
    *,
    options: ReconciliationOptions | None = None,
) -> dict[str, Any]:
    """Score cross-retailer product pairs and return a read-only quality report."""

    options = options or ReconciliationOptions()
    product_list = sorted(
        products,
        key=lambda product: (
            _value(product, "retailer") or "",
            _value(product, "name") or "",
            _value(product, "id") or 0,
        ),
    )
    retailer_counts = Counter(str(_value(product, "retailer")) for product in product_list)
    bucket_counts = Counter(
        {
            "strong_match": 0,
            "candidate": 0,
            "review": 0,
            "below_threshold": 0,
            "blocked": 0,
        }
    )
    blocker_counts: Counter[str] = Counter()
    scored_examples: list[ProductMatchScore] = []
    scored_pair_count = 0

    for index, source in enumerate(product_list):
        for candidate in product_list[index + 1 :]:
            if _value(source, "retailer") == _value(candidate, "retailer"):
                continue

            scored_pair_count += 1
            score = score_product_candidate(
                source,
                candidate,
                threshold=options.candidate_threshold,
                strong_threshold=options.strong_threshold,
            )
            bucket = confidence_bucket(score, review_threshold=options.review_threshold)
            bucket_counts[bucket] += 1
            blocker_counts.update(score.blockers)
            if bucket in {"strong_match", "candidate", "review", "blocked"}:
                scored_examples.append(score)

    examples = sorted(
        scored_examples,
        key=lambda score: (
            _bucket_rank(confidence_bucket(score, review_threshold=options.review_threshold)),
            -score.score,
            _value(score.source, "name") or "",
            _value(score.candidate, "name") or "",
        ),
    )[: options.max_examples]

    return {
        "mode": "read_only_reconciliation",
        "method": RULE_BASED_MATCH_METHOD,
        "thresholds": {
            "strong_match": _decimal_string(options.strong_threshold),
            "candidate": _decimal_string(options.candidate_threshold),
            "review": _decimal_string(options.review_threshold),
        },
        "counts": {
            "retailer_products": len(product_list),
            "retailers": dict(sorted(retailer_counts.items())),
            "scored_cross_retailer_pairs": scored_pair_count,
            "candidate_pairs": bucket_counts["strong_match"] + bucket_counts["candidate"],
            "confidence_buckets": dict(bucket_counts),
            "blockers": dict(sorted(blocker_counts.items())),
        },
        "examples": [_example_payload(score, options=options) for score in examples],
        "notes": _quality_notes(
            retailer_counts=retailer_counts,
            scored_pair_count=scored_pair_count,
            bucket_counts=bucket_counts,
            blocker_counts=blocker_counts,
        ),
    }


def confidence_bucket(
    score: ProductMatchScore,
    *,
    review_threshold: Decimal = REVIEW_THRESHOLD,
) -> str:
    if score.blockers:
        return "blocked"
    if score.is_strong_match:
        return "strong_match"
    if score.is_candidate:
        return "candidate"
    if score.score >= review_threshold:
        return "review"
    return "below_threshold"


def _example_payload(
    score: ProductMatchScore,
    *,
    options: ReconciliationOptions,
) -> dict[str, Any]:
    return {
        "bucket": confidence_bucket(score, review_threshold=options.review_threshold),
        "score": _decimal_string(score.score),
        "blockers": list(score.blockers),
        "source": _product_payload(score.source),
        "candidate": _product_payload(score.candidate),
        "components": [
            {
                "name": component.name,
                "score": _decimal_string(component.score),
                "reason": component.reason,
            }
            for component in score.components
        ],
    }


def _product_payload(product: Any) -> dict[str, Any]:
    return {
        "id": _value(product, "id"),
        "retailer": _value(product, "retailer"),
        "source_product_id": _value(product, "source_product_id"),
        "name": _value(product, "name"),
        "brand": _value(product, "brand"),
        "category": _value(product, "category"),
        "package": {
            "quantity": _decimal_string(_value(product, "normalized_quantity_base")),
            "unit": _value(product, "normalized_unit_base"),
        },
    }


def _quality_notes(
    *,
    retailer_counts: Counter[str],
    scored_pair_count: int,
    bucket_counts: Counter[str],
    blocker_counts: Counter[str],
) -> list[str]:
    notes: list[str] = []
    if len(retailer_counts) < 2:
        notes.append("Need normalized products from at least two retailers before candidates appear.")
    if scored_pair_count == 0:
        notes.append("No cross-retailer pairs were scored.")
    if bucket_counts["review"]:
        notes.append("Review-bucket examples are below the candidate threshold but may inform tuning.")
    if blocker_counts:
        notes.append("Blocked examples show likely false positives prevented by hard rules.")
    if not notes:
        notes.append("Review top examples before storing or acting on match candidates.")
    return notes


def _bucket_rank(bucket: str) -> int:
    order = {
        "strong_match": 0,
        "candidate": 1,
        "review": 2,
        "blocked": 3,
        "below_threshold": 4,
    }
    return order[bucket]


def _value(obj: Any, name: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _decimal_string(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    return str(value)


__all__ = [
    "REVIEW_THRESHOLD",
    "ReconciliationOptions",
    "build_reconciliation_report",
    "confidence_bucket",
]
