import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from app.matching import ReconciliationOptions, build_reconciliation_report

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from reconcile_once import parse_args, validate_args  # noqa: E402


@dataclass(frozen=True)
class ProductFixture:
    id: int
    retailer: str
    source_product_id: str
    name: str
    brand: str | None
    category: str | None
    normalized_quantity_base: Decimal | None
    normalized_unit_base: str | None


def product(
    *,
    id: int = 1,
    retailer: str = "billa",
    source_product_id: str = "billa-ritter-sport",
    name: str = "Ritter Sport Voll-Nuss Schokolade 100 g",
    brand: str | None = "Ritter Sport",
    category: str | None = "Süßwaren Schokolade",
    quantity: Decimal | None = Decimal("0.1000"),
    unit: str | None = "kg",
) -> ProductFixture:
    return ProductFixture(
        id=id,
        retailer=retailer,
        source_product_id=source_product_id,
        name=name,
        brand=brand,
        category=category,
        normalized_quantity_base=quantity,
        normalized_unit_base=unit,
    )


def test_reconciliation_report_counts_strong_cross_retailer_candidates() -> None:
    report = build_reconciliation_report(
        [
            product(),
            product(
                id=2,
                retailer="mpreis",
                source_product_id="mpreis-ritter-sport",
                name="Ritter Sport Alpenvollmilch Voll-Nuss Schokolade 100g",
            ),
        ]
    )

    assert report["counts"]["retailer_products"] == 2
    assert report["counts"]["retailers"] == {"billa": 1, "mpreis": 1}
    assert report["counts"]["scored_cross_retailer_pairs"] == 1
    assert report["counts"]["candidate_pairs"] == 1
    assert report["counts"]["confidence_buckets"]["strong_match"] == 1
    assert report["examples"][0]["bucket"] == "strong_match"
    assert report["examples"][0]["source"]["retailer"] == "billa"
    assert report["examples"][0]["candidate"]["retailer"] == "mpreis"


def test_reconciliation_report_ignores_same_retailer_pairs() -> None:
    report = build_reconciliation_report(
        [
            product(id=1, retailer="billa"),
            product(id=2, retailer="billa", source_product_id="billa-ritter-sport-2"),
        ]
    )

    assert report["counts"]["scored_cross_retailer_pairs"] == 0
    assert report["counts"]["candidate_pairs"] == 0
    assert "Need normalized products from at least two retailers" in report["notes"][0]


def test_reconciliation_report_surfaces_blocked_false_positive_examples() -> None:
    report = build_reconciliation_report(
        [
            product(
                name="Milch 1 l",
                brand=None,
                category="Milchprodukte",
                quantity=Decimal("1.0000"),
                unit="l",
            ),
            product(
                id=2,
                retailer="mpreis",
                source_product_id="mpreis-milch",
                name="Frische Milch 1 l",
                brand=None,
                category="Milchprodukte",
                quantity=Decimal("1.0000"),
                unit="l",
            ),
        ],
        options=ReconciliationOptions(max_examples=1),
    )

    assert report["counts"]["candidate_pairs"] == 0
    assert report["counts"]["confidence_buckets"]["blocked"] == 1
    assert report["counts"]["blockers"] == {"generic_name_without_brand": 1}
    assert report["examples"][0]["bucket"] == "blocked"


def test_reconcile_once_defaults_to_low_volume_local_run() -> None:
    args = parse_args([])

    validate_args(args)

    assert args.limit_per_retailer == 100
    assert args.max_examples == 20


def test_reconcile_once_rejects_oversized_local_run() -> None:
    args = parse_args(["--limit-per-retailer", "501"])

    try:
        validate_args(args)
    except SystemExit as exc:
        assert "500 or lower" in str(exc)
    else:
        raise AssertionError("Expected oversized run to exit")
