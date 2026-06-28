"""Product reconciliation and matching utilities."""

from app.matching.reconciliation import (
    REVIEW_THRESHOLD,
    ReconciliationOptions,
    build_reconciliation_report,
    confidence_bucket,
)
from app.matching.rule_based import (
    CANDIDATE_THRESHOLD,
    RULE_BASED_MATCH_METHOD,
    STRONG_MATCH_THRESHOLD,
    ProductMatchScore,
    ScoreComponent,
    rank_product_candidates,
    score_product_candidate,
)

__all__ = [
    "CANDIDATE_THRESHOLD",
    "REVIEW_THRESHOLD",
    "RULE_BASED_MATCH_METHOD",
    "STRONG_MATCH_THRESHOLD",
    "ProductMatchScore",
    "ReconciliationOptions",
    "ScoreComponent",
    "build_reconciliation_report",
    "confidence_bucket",
    "rank_product_candidates",
    "score_product_candidate",
]
