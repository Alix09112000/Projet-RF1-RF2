import pytest

from app.inputs.calc import balance_warnings, balances
from app.inputs.catalog import B2C1, MODULES, SME1
from app.inputs.timeline import (
    column_letter,
    eur_to_fcfa,
    fcfa_to_eur,
    keur_to_fcfa,
    period_of,
    slot_of_column,
    slots,
)
from tests.fictif_drcom import B2C1_CELLS, SME1_CELLS


def grid(cells):
    out: dict[int, dict[int, float]] = {}
    for c in cells:
        out.setdefault(c["row"], {})[c["slot"]] = c["value"]
    return out


def test_axe_du_temps() -> None:
    s = slots()
    assert len(s) == 24
    assert [x.column for x in (s[0], s[5], s[6], s[11], s[12], s[23])] == [
        "I",
        "N",
        "O",
        "T",
        "U",
        "AF",
    ]
    assert [period_of(i) for i in (0, 5, 6, 11, 12, 23)] == [
        "actual",
        "actual",
        "rf2",
        "rf2",
        "bi",
        "bi",
    ]
    assert slot_of_column("O") == 6 and slot_of_column("AF") == 23
    assert column_letter(32) == "AF"
    with pytest.raises(ValueError):
        slot_of_column("AG")


def test_conversion_fcfa() -> None:
    assert eur_to_fcfa(1) == 655.957
    assert keur_to_fcfa(1) == pytest.approx(655_957)
    assert fcfa_to_eur(655_957) == pytest.approx(1000)


def test_catalogue_conforme_aux_fiches() -> None:
    # « Lignes à saisir » des fiches : 70 lignes B2C1, 63 lignes SME1.
    assert len(B2C1.lines) == 70
    assert len(SME1.lines) == 63
    assert sum(len(line.editable_slots) for line in B2C1.lines) == 1334
    assert sum(len(line.editable_slots) for line in SME1.lines) == 1260
    for module in MODULES.values():
        rows = [line.row for line in module.lines]
        assert len(rows) == len(set(rows)), module.code
        assert module.direction == "DRCOM"


@pytest.mark.parametrize(
    ("row", "first"), [(9, "I"), (15, "O"), (371, "N"), (372, "N"), (119, "I")]
)
def test_periodes_de_saisie_b2c1(row: int, first: str) -> None:
    line = B2C1.line(row)
    assert line is not None and line.first_column == first


def test_soldes_sur_jeu_fictif() -> None:
    b2c = balances(B2C1, grid(B2C1_CELLS))
    assert b2c[30][6] == pytest.approx(0.50)  # START = 1 − 30 % − 20 %
    assert b2c[30][0] is None  # mois réels : mix non saisi
    assert b2c[225][0] == pytest.approx(0.50)
    assert b2c[396][6] == pytest.approx(0.75)  # 1 − 5 × 5 %
    sme = balances(SME1, grid(SME1_CELLS))
    assert sme[18][6] == pytest.approx(0.45)
    assert sme[187][0] == pytest.approx(0.45)
    assert balance_warnings(B2C1, grid(B2C1_CELLS)) == []


def test_solde_negatif_signale() -> None:
    values = {29: {6: 0.7}, 31: {6: 0.5}}
    assert balances(B2C1, values)[30][6] == pytest.approx(-0.2)
    assert "Mix ventes START : solde négatif" in balance_warnings(B2C1, values)[0]
