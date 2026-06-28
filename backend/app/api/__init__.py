"""API routers for Grocery Saver."""

from app.api.comparison import router as comparison_router
from app.api.products import router as products_router

__all__ = ["comparison_router", "products_router"]
