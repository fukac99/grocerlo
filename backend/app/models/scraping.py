from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ScrapeRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ProductMatchReviewStatus(StrEnum):
    UNREVIEWED = "unreviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MANUAL = "manual"


class ScrapeRun(TimestampMixin, Base):
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    retailer: Mapped[str] = mapped_column(String(64), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(
        String(32),
        default=ScrapeRunStatus.PENDING.value,
        nullable=False,
    )
    scraper_version: Mapped[str | None] = mapped_column(String(64))
    source_url: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)

    raw_products: Mapped[list["RawProduct"]] = relationship(back_populates="scrape_run")


class RawProduct(Base):
    __tablename__ = "raw_products"
    __table_args__ = (
        Index("ix_raw_products_retailer_country", "retailer", "country"),
        Index("ix_raw_products_source_product_id", "source_product_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    scrape_run_id: Mapped[int] = mapped_column(ForeignKey("scrape_runs.id"), nullable=False)
    retailer: Mapped[str] = mapped_column(String(64), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    source_product_id: Mapped[str | None] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(Text)
    raw_name: Mapped[str | None] = mapped_column(Text)
    raw_brand: Mapped[str | None] = mapped_column(Text)
    raw_category: Mapped[str | None] = mapped_column(Text)
    raw_price: Mapped[str | None] = mapped_column(String(128))
    raw_old_price: Mapped[str | None] = mapped_column(String(128))
    raw_unit_price: Mapped[str | None] = mapped_column(String(128))
    raw_package_size: Mapped[str | None] = mapped_column(String(128))
    raw_currency: Mapped[str | None] = mapped_column(String(16))
    raw_availability: Mapped[str | None] = mapped_column(Text)
    raw_promotion_text: Mapped[str | None] = mapped_column(Text)
    raw_payload_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    scrape_run: Mapped[ScrapeRun] = relationship(back_populates="raw_products")
    retailer_product: Mapped["RetailerProduct | None"] = relationship(back_populates="raw_product")


class RetailerProduct(Base):
    __tablename__ = "retailer_products"
    __table_args__ = (
        UniqueConstraint("raw_product_id", name="uq_retailer_products_raw_product_id"),
        Index("ix_retailer_products_retailer_country", "retailer", "country"),
        Index("ix_retailer_products_source_product_id", "source_product_id"),
        Index("ix_retailer_products_name", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_product_id: Mapped[int] = mapped_column(ForeignKey("raw_products.id"), nullable=False)
    retailer: Mapped[str] = mapped_column(String(64), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    source_product_id: Mapped[str | None] = mapped_column(String(255))
    product_url: Mapped[str | None] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    brand: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(Text)
    price_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    currency: Mapped[str | None] = mapped_column(String(3))
    unit_price_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    unit_price_unit: Mapped[str | None] = mapped_column(String(32))
    package_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    package_unit: Mapped[str | None] = mapped_column(String(32))
    normalized_quantity_base: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    normalized_unit_base: Mapped[str | None] = mapped_column(String(32))
    price_per_base_unit: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    is_promotion: Mapped[bool] = mapped_column(default=False, nullable=False)
    promotion_type: Mapped[str | None] = mapped_column(String(64))
    availability: Mapped[str | None] = mapped_column(Text)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    raw_product: Mapped[RawProduct] = relationship(back_populates="retailer_product")
    product_matches: Mapped[list["ProductMatch"]] = relationship(back_populates="retailer_product")


class CanonicalProduct(TimestampMixin, Base):
    __tablename__ = "canonical_products"
    __table_args__ = (Index("ix_canonical_products_name_brand", "canonical_name", "canonical_brand"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_name: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_brand: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(Text)

    product_matches: Mapped[list["ProductMatch"]] = relationship(back_populates="canonical_product")


class ProductMatch(Base):
    __tablename__ = "product_matches"
    __table_args__ = (
        UniqueConstraint(
            "canonical_product_id",
            "retailer_product_id",
            name="uq_product_matches_canonical_retailer_product",
        ),
        Index("ix_product_matches_reviewed_status", "reviewed_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_product_id: Mapped[int] = mapped_column(
        ForeignKey("canonical_products.id"),
        nullable=False,
    )
    retailer_product_id: Mapped[int] = mapped_column(
        ForeignKey("retailer_products.id"),
        nullable=False,
    )
    match_confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    match_method: Mapped[str] = mapped_column(String(64), nullable=False)
    reviewed_status: Mapped[str] = mapped_column(
        String(32),
        default=ProductMatchReviewStatus.UNREVIEWED.value,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    canonical_product: Mapped[CanonicalProduct] = relationship(back_populates="product_matches")
    retailer_product: Mapped[RetailerProduct] = relationship(back_populates="product_matches")
