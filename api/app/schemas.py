from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import ImportKind, ImportStatus, Role, VersionStatus


class LoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=255)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: Role
    direction: str | None


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=10, max_length=255)
    role: Role
    direction: str | None = None


class CityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    country: str
    currency: str


class SegmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str


class VersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    label: str
    status: VersionStatus


class ReferenceOut(BaseModel):
    cities: list[CityOut]
    segments: list[SegmentOut]
    versions: list[VersionOut]


class IssueOut(BaseModel):
    message: str
    line: int | None = None
    column: str | None = None


class BatchOut(BaseModel):
    id: int
    kind: ImportKind
    status: ImportStatus
    filename: str
    uploaded_at: datetime
    uploaded_by: str
    rows_read: int
    rows_kept: int
    rows_ignored: int
    months: list[str]
    errors: list[IssueOut]
    warnings: list[IssueOut]
    warnings_confirmed: bool
    decided_at: datetime | None


class ConfirmIn(BaseModel):
    confirm_warnings: bool = False


class SourceStatus(BaseModel):
    last_import_at: datetime | None
    last_import_by: str | None
    last_month: date | None
