from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.client import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    apple_sub: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (UniqueConstraint("refresh_token_hash", name="uq_refresh_token_hash"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    device_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    device_platform: Mapped[str | None] = mapped_column(String(64), nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class WatchlistItem(Base):
    __tablename__ = "watchlist"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    movie_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)


class Catalog(Base):
    __tablename__ = "catalogs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner_user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CatalogItem(Base):
    __tablename__ = "catalog_items"

    catalog_id: Mapped[str] = mapped_column(
        ForeignKey("catalogs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    movie_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    added_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
