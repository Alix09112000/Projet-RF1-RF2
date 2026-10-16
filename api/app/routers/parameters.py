from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.auth.deps import DB, CurrentUser, require_roles
from app.models import CityParameter, ListEntry, Role, User

router = APIRouter(prefix="/parameters", tags=["paramètres"])

Controller = Annotated[User, Depends(require_roles(Role.controller, Role.admin))]

# DROPE1 : D5 = entité légale, D6 = ville. Valeurs choisies dans la table List.
KEYS = {"legal_entity": "Entité légale (DROPE1 D5)", "city": "Ville (DROPE1 D6)"}


class ParametersIn(BaseModel):
    legal_entity: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=120)


def current(db: DB) -> dict[str, str | None]:
    values = {p.key: p.value for p in db.scalars(select(CityParameter))}
    return {key: values.get(key) for key in KEYS}


@router.get("")
def read_parameters(_: CurrentUser, db: DB) -> dict:
    entries = db.scalars(select(ListEntry).order_by(ListEntry.source_row))
    return {
        "values": current(db),
        "labels": KEYS,
        "choices": [
            {"entity": e.entity, "country": e.country, "city": e.city, "source_row": e.source_row}
            for e in entries
        ],
    }


@router.put("")
def save_parameters(body: ParametersIn, user: Controller, db: DB) -> dict:
    pair = db.scalar(
        select(ListEntry).where(ListEntry.entity == body.legal_entity, ListEntry.city == body.city)
    )
    if pair is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Ce couple entité légale / ville n'existe pas dans la table List",
        )
    now = datetime.now(UTC)
    for key, value in (("legal_entity", body.legal_entity), ("city", body.city)):
        param = db.scalar(select(CityParameter).where(CityParameter.key == key))
        if param is None:
            db.add(CityParameter(key=key, value=value, updated_by_id=user.id, updated_at=now))
        else:
            param.value, param.updated_by_id, param.updated_at = value, user.id, now
    db.commit()
    return {"values": current(db)}
