"""Moteur B2C1 B0–B2 sur jeu fictif (aucune donnée Canalbox)."""

from datetime import date

import pytest

from app.engine.b2c1 import add_months, checks, run, working_days

FIRST = date(2025, 1, 1)  # colonne I ; l'année ne change pas le calcul, seulement le calendrier


def actuals(months: int = 6, start: date = date(2024, 7, 1)) -> dict[str, dict[date, float]]:
    keys = ("Ventes_premium", "Ventes_Start", "Ventes_Fit")
    data: dict[str, dict[date, float]] = {k: {} for k in keys}
    for i in range(months):
        m = add_months(start, i)
        data["Ventes_premium"][m] = 10.0 + i
        data["Ventes_Start"][m] = 20.0
        data["Ventes_Fit"][m] = 5.0
    return data


def forecast_grid() -> dict[int, dict[int, float]]:
    grid: dict[int, dict[int, float]] = {}
    for slot in range(6, 24):
        for row, value in ((15, 40), (16, 30), (17, 20), (18, 10), (29, 0.3), (31, 0.2)):
            grid.setdefault(row, {})[slot] = value
        grid.setdefault(59, {})[slot] = 4
        grid.setdefault(49, {})[slot] = 2
    return grid


def test_t1_jours_ouvres() -> None:
    assert working_days(date(2025, 3, 1), 0) == 26  # 31 jours, 5 dimanches
    assert working_days(date(2025, 2, 1), 1) == 23  # 28 jours, 4 dimanches, 1 congé
    assert working_days(date(2025, 6, 1), 40) == 0  # congés = mois entier


def test_t2_ventes_reel_puis_prevision() -> None:
    res = run(FIRST, forecast_grid(), actuals(12))
    # Réel (janvier 2025 = 7e mois du jeu) : lu dans la source.
    assert res.get("gross_adds.PREMIUM", 0) == 16
    assert res.get("gross_adds.total", 0) == 41
    # Prévision : 100 ventes ; 30 % / 50 % / 20 %.
    assert res.get("gross_adds.total", 6) == 100
    assert res.get("gross_adds.START", 6) == pytest.approx(50)
    assert checks(res) == []


def test_t2_cumul_depuis_origine() -> None:
    data = actuals(12)
    res = run(FIRST, forecast_grid(), data)
    before = sum(v for m, v in data["Ventes_premium"].items() if m < FIRST)
    assert res.get("gross_adds.cumul.PREMIUM", 0) == before + 16
    assert res.get("gross_adds.cumul.PREMIUM", 6) == pytest.approx(
        res.get("gross_adds.cumul.PREMIUM", 5) + 30
    )
    total = sum(res.get(f"gross_adds.cumul.{r}", 23) for r in ("PREMIUM", "START", "FIT"))
    assert res.get("gross_adds.cumul.total", 23) == pytest.approx(total)


def test_t8_cas_limites() -> None:
    res = run(FIRST, {}, {})
    assert res.get("gross_adds.total", 10) == 0
    assert res.get("productivity.Internal VAD D2D.per_seller_day", 10) == 0
    assert "6 mois réels sans données" in res.warnings[0]


def test_productivite() -> None:
    res = run(FIRST, forecast_grid(), actuals(12))
    days = res.get("calendar.working_days", 6)
    per_day = res.get("productivity.Internal VAD D2D.per_seller_day", 6)
    assert per_day == pytest.approx(40 / 4 / days)
    assert res.get("productivity.Internal VAD D2D.per_supervisor", 6) == 20


def test_mix_depasse_100() -> None:
    grid = forecast_grid()
    grid[29][6] = 0.9
    res = run(FIRST, grid, {})
    assert any("dépasse 100 %" in w for w in res.warnings)
