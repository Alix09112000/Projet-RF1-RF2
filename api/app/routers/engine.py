from datetime import date

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.auth.deps import DB, CurrentUser
from app.engine import b2c1
from app.imports.spec import CITY
from app.models import ActualValue, ImportKind
from app.routers.inputs import get_version, load_grid

router = APIRouter(prefix="/engine", tags=["moteur"])


@router.get("/{version_code}/B2C1")
def run_b2c1(version_code: str, first_month: date, _: CurrentUser, db: DB) -> dict:
    """first_month : mois de la colonne I (premier des 6 mois réels), au format AAAA-MM-01."""
    if first_month.day != 1:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Le mois doit être un 1er.")
    version = get_version(db, version_code)
    grid = load_grid(db, version.id, "B2C1")
    actuals: dict[str, dict[date, float]] = {}
    for value in db.scalars(
        select(ActualValue).where(
            ActualValue.source == ImportKind.commercial, ActualValue.city_code == CITY
        )
    ):
        actuals.setdefault(value.metric, {})[value.month] = value.value
    result = b2c1.run(first_month, grid, actuals)
    return {
        "version": version.code,
        "months": [m.isoformat() for m in result.months],
        "series": result.series,
        "warnings": result.warnings,
        "checks": b2c1.checks(result),
    }
