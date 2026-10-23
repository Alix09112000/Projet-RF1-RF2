from datetime import date

from sqlalchemy import delete, func, insert, select
from sqlalchemy.orm import Session

from app.imports.spec import CITY, ECHUS_SERIES, VARIATION_METRICS
from app.models import ActualValue, ImportBatch, ImportKind


def load_context(db: Session, kind: ImportKind) -> tuple[set[date], dict[str, dict[date, float]]]:
    """Mois déjà importés, et valeurs utiles au contrôle de variation."""
    months = set(db.scalars(select(ActualValue.month).where(ActualValue.source == kind).distinct()))
    previous: dict[str, dict[date, float]] = {}
    if kind == ImportKind.commercial:
        rows = db.execute(
            select(ActualValue.metric, ActualValue.month, ActualValue.value).where(
                ActualValue.source == kind, ActualValue.metric.in_(VARIATION_METRICS)
            )
        ).all()
        for metric, month, value in rows:
            previous.setdefault(metric, {})[month] = value
    else:
        totals = db.execute(
            select(ActualValue.month, func.sum(ActualValue.value))
            .where(ActualValue.source == kind)
            .group_by(ActualValue.month)
        ).all()
        previous[ECHUS_SERIES] = {month: float(total) for month, total in totals}
    return months, previous


def apply_batch(db: Session, batch: ImportBatch) -> None:
    """Remplace les mois du dépôt par ses valeurs. Le commit est fait par l'appelant."""
    months = [date.fromisoformat(m) for m in batch.months]
    db.execute(
        delete(ActualValue).where(
            ActualValue.source == batch.kind,
            ActualValue.city_code == CITY,
            ActualValue.month.in_(months),
        )
    )
    records = batch.records or []
    if records:
        db.execute(
            insert(ActualValue),
            [
                {
                    "source": batch.kind,
                    "city_code": r["city"],
                    "month": date.fromisoformat(r["month"]),
                    "metric": r["metric"],
                    "seniority": r["seniority"],
                    "value": r["value"],
                    "batch_id": batch.id,
                }
                for r in records
            ],
        )
