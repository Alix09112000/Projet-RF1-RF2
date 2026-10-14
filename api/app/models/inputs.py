from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.user import User


def _now() -> datetime:
    return datetime.now(UTC)


class AssumptionValue(Base):
    """Une cellule beige : version × module × ligne Excel × mois (slot 0 à 23)."""

    __tablename__ = "assumption_values"
    __table_args__ = (
        UniqueConstraint("version_id", "module", "row", "slot", name="uq_assumption_cell"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("forecast_versions.id"))
    module: Mapped[str] = mapped_column(String(16))
    row: Mapped[int] = mapped_column(Integer)
    slot: Mapped[int] = mapped_column(Integer)
    value: Mapped[float] = mapped_column(Float)
    updated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AssumptionChange(Base):
    """Historique : chaque modification d'une cellule, jamais effacée."""

    __tablename__ = "assumption_changes"
    __table_args__ = (Index("ix_assumption_changes_cell", "version_id", "module", "row"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("forecast_versions.id"))
    module: Mapped[str] = mapped_column(String(16))
    row: Mapped[int] = mapped_column(Integer)
    slot: Mapped[int] = mapped_column(Integer)
    old_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    new_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(lazy="joined")
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CityParameter(Base):
    """Paramètres de la ville (DROPE1 D5 entité légale, D6 ville)."""

    __tablename__ = "city_parameters"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(32), unique=True)
    value: Mapped[str] = mapped_column(String(255))
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ListEntry(Base):
    """Table List : entités du groupe (entité légale / pays / ville)."""

    __tablename__ = "list_entries"
    __table_args__ = (UniqueConstraint("entity", "city", name="uq_list_entry"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    entity: Mapped[str] = mapped_column(String(120))
    country: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(120))
    source_row: Mapped[int] = mapped_column(Integer)
