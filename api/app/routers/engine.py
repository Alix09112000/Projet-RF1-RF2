from datetime import date

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.auth.deps import DB, CurrentUser
from app.engine import b2c1
from app.imports.spec import CITY
from app.inputs.timeline import real_months
from app.models import ActualValue, ImportKind
from app.routers.inputs import get_version, load_grid
from app.routers.parameters import reference_month

router = APIRouter(prefix="/engine", tags=["moteur"])


@router.get("/{version_code}/B2C1")
def run_b2c1(version_code: str, _: CurrentUser, db: DB, first_month: date | None = None) -> dict:
    """Janvier de l'exercice = colonne I. Réel = janvier au mois précédant le mois de référence
    (Paramètres). first_month (AAAA-MM-01) force un autre début d'axe."""
    reference = reference_month(db)
    if first_month is None:
        first_month = date(reference.year, 1, 1)
    if first_month.day != 1:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Le mois doit être un 1er.")
    n_real = real_months(reference)
    version = get_version(db, version_code)
    grid = load_grid(db, version.id, "B2C1")
    actuals: dict[str, dict[date, float]] = {}
    for value in db.scalars(
        select(ActualValue).where(
            ActualValue.source == ImportKind.commercial, ActualValue.city_code == CITY
        )
    ):
        actuals.setdefault(value.metric, {})[value.month] = value.value
    result = b2c1.run(first_month, grid, actuals, n_real)
    return {
        "version": version.code,
        "reference_month": reference.strftime("%Y-%m"),
        "real_months": n_real,
        "months": [m.isoformat() for m in result.months],
        "series": result.series,
        "warnings": result.warnings,
        "checks": b2c1.checks(result),
    }
