import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class VersionStatus(enum.StrEnum):
    draft = "draft"
    published = "published"
    archived = "archived"


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(8), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    country: Mapped[str] = mapped_column(String(120))
    currency: Mapped[str] = mapped_column(String(8))


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    name: Mapped[str] = mapped_column(String(120))


class ForecastVersion(Base):
    """Un exercice de prévision : BI26, RF1, RF2…"""

    __tablename__ = "forecast_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True)
    label: Mapped[str] = mapped_column(String(120))
    status: Mapped[VersionStatus] = mapped_column(
        Enum(VersionStatus, native_enum=False, length=20), default=VersionStatus.draft
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
