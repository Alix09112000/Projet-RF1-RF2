from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import DB, CurrentUser
from app.inputs.calc import balance_warnings, balances
from app.inputs.catalog import MODULES, Module, note
from app.inputs.timeline import slots
from app.models import (
    AssumptionChange,
    AssumptionValue,
    ForecastVersion,
    Role,
    User,
    VersionStatus,
)

router = APIRouter(prefix="/inputs", tags=["saisie"])


class CellIn(BaseModel):
    row: int
    slot: int = Field(ge=0, le=23)
    value: float | None  # None = effacer la cellule


class SaveIn(BaseModel):
    cells: list[CellIn] = Field(min_length=1, max_length=2000)
    comment: str | None = Field(default=None, max_length=1000)


def get_module(code: str) -> Module:
    module = MODULES.get(code.upper())
    if module is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Module inconnu")
    return module


def get_version(db: Session, code: str) -> ForecastVersion:
    version = db.scalar(select(ForecastVersion).where(ForecastVersion.code == code.upper()))
    if version is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Version inconnue")
    return version


def can_edit(user: User, module: Module) -> bool:
    if user.role in (Role.admin, Role.controller):
        return True
    return user.role == Role.contributor and (user.direction or "").upper() == module.direction


def load_grid(db: Session, version_id: int, module: str) -> dict[int, dict[int, float]]:
    grid: dict[int, dict[int, float]] = {}
    for cell in db.scalars(
        select(AssumptionValue).where(
            AssumptionValue.version_id == version_id, AssumptionValue.module == module
        )
    ):
        grid.setdefault(cell.row, {})[cell.slot] = cell.value
    return grid


@router.get("/modules")
def list_modules(_: CurrentUser) -> list[dict[str, object]]:
    return [
        {"code": m.code, "name": m.name, "direction": m.direction, "lines": len(m.lines)}
        for m in MODULES.values()
    ]


@router.get("/{version_code}/{module_code}")
def read_module(version_code: str, module_code: str, user: CurrentUser, db: DB) -> dict:
    module = get_module(module_code)
    version = get_version(db, version_code)
    grid = load_grid(db, version.id, module.code)
    return {
        "module": module.code,
        "name": module.name,
        "direction": module.direction,
        "version": version.code,
        "editable": version.status == VersionStatus.draft and can_edit(user, module),
        "slots": [s.__dict__ for s in slots()],
        "lines": [
            {
                "row": line.row,
                "label": line.label,
                "unit": line.unit,
                "nature": line.nature,
                "section": line.section,
                "first_slot": line.first_slot,
                "note": note(module.code, line.row),
                "values": [grid.get(line.row, {}).get(i) for i in range(24)],
            }
            for line in module.lines
        ],
        "balances": [
            {"row": b.row, "label": b.label, "parts": list(b.parts), "confirmed": b.confirmed,
             "values": balances(module, grid)[b.row]}
            for b in module.balances
        ],
        "warnings": balance_warnings(module, grid),
    }


@router.put("/{version_code}/{module_code}")
def save_module(
    version_code: str, module_code: str, body: SaveIn, user: CurrentUser, db: DB
) -> dict:
    module = get_module(module_code)
    version = get_version(db, version_code)
    if version.status != VersionStatus.draft:
        raise HTTPException(status.HTTP_409_CONFLICT, f"La version {version.code} est figée")
    if not can_edit(user, module):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, f"Saisie réservée à la direction {module.direction}"
        )

    errors = []
    for cell in body.cells:
        line = module.line(cell.row)
        if line is None:
            errors.append(f"Ligne {cell.row} : pas une cellule de saisie de {module.code}.")
        elif cell.slot < line.first_slot:
            errors.append(
                f"Ligne {cell.row} ({line.label}) : mois {cell.slot + 1} non saisissable, "
                f"saisie à partir de la colonne {line.first_column}."
            )
    if errors:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, errors)

    existing = {
        (c.row, c.slot): c
        for c in db.scalars(
            select(AssumptionValue).where(
                AssumptionValue.version_id == version.id, AssumptionValue.module == module.code
            )
        )
    }
    now = datetime.now(UTC)
    changed = 0
    for cell in body.cells:
        current = existing.get((cell.row, cell.slot))
        old = current.value if current else None
        if old == cell.value:
            continue
        if cell.value is None and current is not None:
            db.delete(current)
        elif current is not None and cell.value is not None:
            current.value, current.updated_by_id, current.updated_at = cell.value, user.id, now
        elif cell.value is not None:
            db.add(AssumptionValue(version_id=version.id, module=module.code, row=cell.row,
                                   slot=cell.slot, value=cell.value, updated_by_id=user.id,
                                   updated_at=now))
        db.add(AssumptionChange(version_id=version.id, module=module.code, row=cell.row,
                                slot=cell.slot, old_value=old, new_value=cell.value,
                                comment=body.comment, user_id=user.id, changed_at=now))
        changed += 1
    db.commit()
    grid = load_grid(db, version.id, module.code)
    return {"changed": changed, "warnings": balance_warnings(module, grid)}


@router.get("/{version_code}/{module_code}/history")
def history(
    version_code: str,
    module_code: str,
    _: CurrentUser,
    db: DB,
    row: int | None = None,
) -> list[dict]:
    module = get_module(module_code)
    version = get_version(db, version_code)
    query = select(AssumptionChange).where(
        AssumptionChange.version_id == version.id, AssumptionChange.module == module.code
    )
    if row is not None:
        query = query.where(AssumptionChange.row == row)
    changes = db.scalars(query.order_by(AssumptionChange.id.desc()).limit(500))
    labels = {line.row: line.label for line in module.lines}
    return [
        {
            "row": c.row,
            "label": labels.get(c.row, ""),
            "slot": c.slot,
            "old_value": c.old_value,
            "new_value": c.new_value,
            "comment": c.comment,
            "user": c.user.full_name,
            "changed_at": c.changed_at.isoformat(),
        }
        for c in changes
    ]
