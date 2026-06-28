"""Product reconciliation and matching utilities."""

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
    "RULE_BASED_MATCH_METHOD",
    "STRONG_MATCH_THRESHOLD",
    "ProductMatchScore",
    "ScoreComponent",
    "rank_product_candidates",
    "score_product_candidate",
]
