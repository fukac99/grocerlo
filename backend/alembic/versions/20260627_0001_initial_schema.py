"""Initial grocery saver schema.

Revision ID: 20260627_0001
Revises:
Create Date: 2026-06-27
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260627_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "scrape_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("retailer", sa.String(length=64), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("scraper_version", sa.String(length=64), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "canonical_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("canonical_name", sa.Text(), nullable=False),
        sa.Column("canonical_brand", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "raw_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scrape_run_id", sa.Integer(), nullable=False),
        sa.Column("retailer", sa.String(length=64), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("source_product_id", sa.String(length=255), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("raw_name", sa.Text(), nullable=True),
        sa.Column("raw_brand", sa.Text(), nullable=True),
        sa.Column("raw_category", sa.Text(), nullable=True),
        sa.Column("raw_price", sa.String(length=128), nullable=True),
        sa.Column("raw_old_price", sa.String(length=128), nullable=True),
        sa.Column("raw_unit_price", sa.String(length=128), nullable=True),
        sa.Column("raw_package_size", sa.String(length=128), nullable=True),
        sa.Column("raw_currency", sa.String(length=16), nullable=True),
        sa.Column("raw_availability", sa.Text(), nullable=True),
        sa.Column("raw_promotion_text", sa.Text(), nullable=True),
        sa.Column(
            "raw_payload_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["scrape_run_id"], ["scrape_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "retailer_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("raw_product_id", sa.Integer(), nullable=False),
        sa.Column("retailer", sa.String(length=64), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("source_product_id", sa.String(length=255), nullable=True),
        sa.Column("product_url", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("brand", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("price_amount", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("unit_price_amount", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("unit_price_unit", sa.String(length=32), nullable=True),
        sa.Column("package_quantity", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("package_unit", sa.String(length=32), nullable=True),
        sa.Column("normalized_quantity_base", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("normalized_unit_base", sa.String(length=32), nullable=True),
        sa.Column("price_per_base_unit", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("is_promotion", sa.Boolean(), nullable=False),
        sa.Column("promotion_type", sa.String(length=64), nullable=True),
        sa.Column("availability", sa.Text(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["raw_product_id"], ["raw_products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("raw_product_id", name="uq_retailer_products_raw_product_id"),
    )

    op.create_table(
        "product_matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("canonical_product_id", sa.Integer(), nullable=False),
        sa.Column("retailer_product_id", sa.Integer(), nullable=False),
        sa.Column("match_confidence", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("match_method", sa.String(length=64), nullable=False),
        sa.Column("reviewed_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["canonical_product_id"], ["canonical_products.id"]),
        sa.ForeignKeyConstraint(["retailer_product_id"], ["retailer_products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "canonical_product_id",
            "retailer_product_id",
            name="uq_product_matches_canonical_retailer_product",
        ),
    )

    op.create_index(
        "ix_canonical_products_name_brand",
        "canonical_products",
        ["canonical_name", "canonical_brand"],
    )
    op.create_index("ix_product_matches_reviewed_status", "product_matches", ["reviewed_status"])
    op.create_index("ix_raw_products_retailer_country", "raw_products", ["retailer", "country"])
    op.create_index("ix_raw_products_source_product_id", "raw_products", ["source_product_id"])
    op.create_index("ix_retailer_products_name", "retailer_products", ["name"])
    op.create_index(
        "ix_retailer_products_retailer_country",
        "retailer_products",
        ["retailer", "country"],
    )
    op.create_index(
        "ix_retailer_products_source_product_id",
        "retailer_products",
        ["source_product_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_retailer_products_source_product_id", table_name="retailer_products")
    op.drop_index("ix_retailer_products_retailer_country", table_name="retailer_products")
    op.drop_index("ix_retailer_products_name", table_name="retailer_products")
    op.drop_index("ix_raw_products_source_product_id", table_name="raw_products")
    op.drop_index("ix_raw_products_retailer_country", table_name="raw_products")
    op.drop_index("ix_product_matches_reviewed_status", table_name="product_matches")
    op.drop_index("ix_canonical_products_name_brand", table_name="canonical_products")
    op.drop_table("product_matches")
    op.drop_table("retailer_products")
    op.drop_table("raw_products")
    op.drop_table("canonical_products")
    op.drop_table("scrape_runs")
