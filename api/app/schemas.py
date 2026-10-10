from pydantic import BaseModel, ConfigDict, Field

from app.models import Role, VersionStatus


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
