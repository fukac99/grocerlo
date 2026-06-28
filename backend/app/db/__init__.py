"""Database setup, session helpers, and data access utilities."""

from app.db.comparison import (
    COMPARISON_MATCH_STATUSES,
    CanonicalProductComparison,
    build_canonical_comparison_statement,
    search_canonical_product_comparisons,
)
from app.db.product_search import (
    BILLA_RETAILER,
    DEFAULT_SEARCH_LIMIT,
    MAX_SEARCH_LIMIT,
    build_billa_product_search_statement,
    normalize_product_search_terms,
    search_billa_products,
)
from app.db.retailer_products import (
    RetailerProductNormalizationResult,
    SkippedRawProduct,
    normalize_retailer_products_for_scrape_run,
)

__all__ = [
    "BILLA_RETAILER",
    "COMPARISON_MATCH_STATUSES",
    "CanonicalProductComparison",
    "DEFAULT_SEARCH_LIMIT",
    "MAX_SEARCH_LIMIT",
    "RetailerProductNormalizationResult",
    "SkippedRawProduct",
    "build_canonical_comparison_statement",
    "build_billa_product_search_statement",
    "normalize_product_search_terms",
    "normalize_retailer_products_for_scrape_run",
    "search_billa_products",
    "search_canonical_product_comparisons",
]
