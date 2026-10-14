"""Calculs déjà établis par les fiches pour la saisie (le moteur B2C1 viendra ensuite)."""

from collections.abc import Mapping

from app.inputs.catalog import Module
from app.inputs.timeline import SLOTS

Grid = Mapping[int, Mapping[int, float]]  # ligne → slot → valeur


def balances(module: Module, values: Grid) -> dict[int, list[float | None]]:
    """Soldes 1 − Σ parts, par mois. None si aucune des parts n'est saisie ce mois-là."""
    out: dict[int, list[float | None]] = {}
    for balance in module.balances:
        series: list[float | None] = []
        for slot in range(SLOTS):
            parts = [values.get(row, {}).get(slot) for row in balance.parts]
            known = [p for p in parts if p is not None]
            series.append(None if not known else round(1 - sum(known), 10))
        out[balance.row] = series
    return out


def balance_warnings(module: Module, values: Grid) -> list[str]:
    """Un solde négatif signifie que les parts saisies dépassent 100 %."""
    warnings = []
    for balance in module.balances:
        for slot, value in enumerate(balances(module, values)[balance.row]):
            if value is not None and value < 0:
                warnings.append(
                    f"{balance.label} : solde négatif ({value:.0%}) au mois {slot + 1}."
                )
    return warnings
