import sys
from argparse import Namespace
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from scrape_once import validate_storage_policy  # noqa: E402


def test_validate_storage_policy_allows_capped_mpreis_store() -> None:
    args = Namespace(retailer="mpreis", store=True, limit_categories=1, max_products=3)

    validate_storage_policy(args)


def test_validate_storage_policy_rejects_broad_mpreis_store_pages() -> None:
    args = Namespace(retailer="mpreis", store=True, limit_categories=2, max_products=3)

    try:
        validate_storage_policy(args)
    except SystemExit as exc:
        assert str(exc) == "MPREIS stored validation is capped at exactly 1 category-equivalent page."
    else:
        raise AssertionError("Expected broad MPREIS stored category scope to exit")


def test_validate_storage_policy_rejects_broad_mpreis_store_products() -> None:
    args = Namespace(retailer="mpreis", store=True, limit_categories=1, max_products=4)

    try:
        validate_storage_policy(args)
    except SystemExit as exc:
        assert str(exc) == "MPREIS stored validation is capped at 3 raw products."
    else:
        raise AssertionError("Expected broad MPREIS stored product scope to exit")


def test_validate_storage_policy_ignores_billa_store() -> None:
    args = Namespace(retailer="billa", store=True, limit_categories=2, max_products=50)

    validate_storage_policy(args)
