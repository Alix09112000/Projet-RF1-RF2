import enum
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.user import User


class ImportKind(enum.StrEnum):
    commercial = "commercial"
    echus = "echus"


class ImportStatus(enum.StrEnum):
    pending = "pending"  # vérifié, en attente de confirmation
    accepted = "accepted"
    rejected = "rejected"  # erreurs bloquantes : rien n'est enregistré
    cancelled = "cancelled"


def _now() -> datetime:
    return datetime.now(UTC)


class ImportBatch(Base):
    """Un dépôt de fichier, accepté ou non. Le fichier d'origine est conservé."""

    __tablename__ = "import_batches"
    __table_args__ = (Index("ix_import_batches_kind_status", "kind", "status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[ImportKind] = mapped_column(Enum(ImportKind, native_enum=False, length=20))
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus, native_enum=False, length=20))
    filename: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[int] = mapped_column(Integer)
    file_sha256: Mapped[str] = mapped_column(String(64))
    content: Mapped[bytes] = mapped_column(LargeBinary)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    uploaded_by: Mapped[User] = relationship(lazy="joined")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rows_read: Mapped[int] = mapped_column(Integer, default=0)
    rows_kept: Mapped[int] = mapped_column(Integer, default=0)
    rows_ignored: Mapped[int] = mapped_column(Integer, default=0)
    months: Mapped[list[str]] = mapped_column(JSON, default=list)
    errors: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    warnings: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    records: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    warnings_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)


class ActualValue(Base):
    """Une valeur réalisée : source × ville × mois × indicateur (× ancienneté pour les échus)."""

    __tablename__ = "actual_values"
    __table_args__ = (
        UniqueConstraint(
            "source", "city_code", "month", "metric", "seniority", name="uq_actual_value"
        ),
        Index("ix_actual_values_source_month", "source", "month"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[ImportKind] = mapped_column(Enum(ImportKind, native_enum=False, length=20))
    city_code: Mapped[str] = mapped_column(String(8))
    month: Mapped[date] = mapped_column(Date)
    metric: Mapped[str] = mapped_column(String(64))
    seniority: Mapped[int] = mapped_column(Integer, default=0)
    value: Mapped[float] = mapped_column(Float)
    batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id"))
