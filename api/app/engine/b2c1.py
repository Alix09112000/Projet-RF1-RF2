"""Moteur B2C1, blocs B0 à B2 (document « Moteur B2C_1 en blocs de codage »).

Option B retenue : les équations du Moteur, branchées sur les colonnes réelles de Source BR PBI
(38 colonnes A–AL), par libellé. Les lignes de saisie sont celles de la fiche B2C1 (catalogue).
Le calcul avance mois par mois (24 slots : 6 réels, 6 RF2, 12 BI).

Sorties : un dictionnaire clé → 24 valeurs. Les clés sont textuelles (règle 3), pas des lignes.
"""

import calendar
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date

from app.inputs.timeline import DEFAULT_REAL, SLOTS

Grid = Mapping[int, Mapping[int, float]]  # ligne de saisie B2C1 → slot → valeur
Actuals = Mapping[str, Mapping[date, float]]  # colonne Source BR PBI → mois → valeur

RANGES = ("PREMIUM", "START", "FIT")

# Source BR PBI, colonnes réelles (lettre du fichier reçu) ↔ colonne citée par le Moteur.
SOURCE_SALES = {"PREMIUM": "Ventes_premium", "START": "Ventes_Start", "FIT": "Ventes_Fit"}  # D E F

# Saisies (fiche B2C1, « Lignes à saisir »).
ROW_HOLIDAYS = 9
CHANNELS = {  # canal → (ligne ventes, ligne effectif vendeurs, ligne superviseurs)
    "Internal VAD D2D": (15, 59, 49),
    "Internal VAD SiS": (16, 60, 50),
    "External VAD D2D": (17, 61, 51),
    "Distribution Network": (18, 70, None),  # effectif = points de vente actifs
}
ROW_MIX = {"PREMIUM": 29, "FIT": 31}  # START = 1 − PREMIUM − FIT


def add_months(d: date, n: int) -> date:
    years, month0 = divmod(d.month - 1 + n, 12)
    return date(d.year + years, month0 + 1, 1)


def _div(a: float, b: float) -> float:
    """Règle du Moteur : 0 si division impossible (T8)."""
    return a / b if b else 0.0


@dataclass
class Result:
    months: list[date]
    series: dict[str, list[float]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    n_real: int = DEFAULT_REAL

    def put(self, key: str, slot: int, value: float) -> None:
        self.series.setdefault(key, [0.0] * SLOTS)[slot] = value

    def get(self, key: str, slot: int) -> float:
        return self.series.get(key, [0.0] * SLOTS)[slot] if 0 <= slot < SLOTS else 0.0


def _input(grid: Grid, row: int, slot: int) -> float:
    return grid.get(row, {}).get(slot, 0.0)


# B0 — Calendrier --------------------------------------------------------------------------------


def working_days(month: date, holidays: float) -> float:
    """NETWORKDAYS.INTL code 11 : tous les jours sauf le dimanche, moins les congés saisis."""
    days = calendar.monthrange(month.year, month.month)[1]
    sundays = sum(1 for d in range(1, days + 1) if date(month.year, month.month, d).weekday() == 6)
    return max(days - sundays - holidays, 0.0)


def block_b0(res: Result, grid: Grid, slot: int) -> None:
    m = res.months[slot]
    res.put("calendar.days", slot, calendar.monthrange(m.year, m.month)[1])
    res.put("calendar.holidays", slot, _input(grid, ROW_HOLIDAYS, slot))
    res.put("calendar.working_days", slot, working_days(m, _input(grid, ROW_HOLIDAYS, slot)))


# B1 — Ventes brutes -----------------------------------------------------------------------------


def opening_cumul(actuals: Actuals, before: date) -> dict[str, float]:
    """Cumul des ventes depuis l'origine jusqu'au mois précédent (recalcul des colonnes AI–AL)."""
    return {
        r: sum(v for m, v in actuals.get(SOURCE_SALES[r], {}).items() if m < before) for r in RANGES
    }


def block_b1(res: Result, grid: Grid, actuals: Actuals, slot: int) -> None:
    m = res.months[slot]
    if slot < res.n_real:
        # Réel : ventes par gamme lues dans la source ; total = somme des gammes (point ouvert 2).
        for r in RANGES:
            res.put(f"gross_adds.{r}", slot, actuals.get(SOURCE_SALES[r], {}).get(m, 0.0))
        for name, (row, _, _) in CHANNELS.items():
            res.put(f"gross_adds.channel.{name}", slot, _input(grid, row, slot))
        total = sum(res.get(f"gross_adds.{r}", slot) for r in RANGES)
        for r in RANGES:  # mix constaté = part de chaque gamme dans le total du mois
            res.put(f"gross_adds.mix.{r}", slot, _div(res.get(f"gross_adds.{r}", slot), total))
    else:
        # Prévision : total = somme des 4 canaux ; gamme = total × % ; START = solde.
        total = 0.0
        for name, (row, _, _) in CHANNELS.items():
            value = _input(grid, row, slot)
            res.put(f"gross_adds.channel.{name}", slot, value)
            total += value
        premium, fit = (_input(grid, ROW_MIX[r], slot) for r in ("PREMIUM", "FIT"))
        start = 1 - premium - fit
        if start < 0:
            res.warnings.append(f"{m:%m/%Y} : % PREMIUM + % FIT dépasse 100 %.")
        for r, share in (("PREMIUM", premium), ("START", start), ("FIT", fit)):
            res.put(f"gross_adds.mix.{r}", slot, share)
            res.put(f"gross_adds.{r}", slot, total * share)
    res.put("gross_adds.total", slot, total)

    for r in RANGES:
        previous = (
            res.get(f"gross_adds.cumul.{r}", slot - 1)
            if slot > 0
            else res.series["_opening"][RANGES.index(r)]
        )
        res.put(f"gross_adds.cumul.{r}", slot, previous + res.get(f"gross_adds.{r}", slot))
    res.put(
        "gross_adds.cumul.total", slot, sum(res.get(f"gross_adds.cumul.{r}", slot) for r in RANGES)
    )


# B2 — Productivité commerciale (contrôle, sans impact en aval) ---------------------------------


def block_b2(res: Result, grid: Grid, slot: int) -> None:
    days = res.get("calendar.working_days", slot)
    for name, (_, staff_row, supervisor_row) in CHANNELS.items():
        sales = res.get(f"gross_adds.channel.{name}", slot)
        staff = _input(grid, staff_row, slot)
        res.put(f"productivity.{name}.per_seller_day", slot, _div(_div(sales, staff), days))
        if supervisor_row is not None:
            supervisors = _input(grid, supervisor_row, slot)
            res.put(f"productivity.{name}.per_supervisor", slot, _div(sales, supervisors))


# Boucle -----------------------------------------------------------------------------------------


def run(first_month: date, grid: Grid, actuals: Actuals, n_real: int = DEFAULT_REAL) -> Result:
    """first_month = mois de la colonne I (janvier) ; n_real = nombre de mois réels."""
    first_month = date(first_month.year, first_month.month, 1)
    res = Result(months=[add_months(first_month, i) for i in range(SLOTS)], n_real=n_real)
    opening = opening_cumul(actuals, first_month)
    res.series["_opening"] = [opening[r] for r in RANGES]
    missing = [m for m in res.months[:n_real] if m not in actuals.get("Ventes_premium", {})]
    if missing:
        res.warnings.append(
            f"{len(missing)} mois réels sans données Source BR PBI : ventes comptées à 0."
        )
    for slot in range(SLOTS):
        block_b0(res, grid, slot)
        block_b1(res, grid, actuals, slot)
        block_b2(res, grid, slot)
    del res.series["_opening"]
    return res


def checks(res: Result) -> list[str]:
    """Tests de cohérence du Moteur (T2) : somme des gammes = total, somme des % = 100 %."""
    errors = []
    for slot in range(SLOTS):
        parts = sum(res.get(f"gross_adds.{r}", slot) for r in RANGES)
        if abs(parts - res.get("gross_adds.total", slot)) > 1e-9:
            errors.append(f"Slot {slot} : somme des gammes ≠ total.")
        if slot >= res.n_real:
            mix = sum(res.get(f"gross_adds.mix.{r}", slot) for r in RANGES)
            if abs(mix - 1) > 1e-9:
                errors.append(f"Slot {slot} : somme des % ≠ 100 %.")
    return errors
