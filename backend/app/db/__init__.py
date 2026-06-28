"""Database setup, session helpers, and data access utilities."""

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
    "DEFAULT_SEARCH_LIMIT",
    "MAX_SEARCH_LIMIT",
    "RetailerProductNormalizationResult",
    "SkippedRawProduct",
    "build_billa_product_search_statement",
    "normalize_product_search_terms",
    "normalize_retailer_products_for_scrape_run",
    "search_billa_products",
]
