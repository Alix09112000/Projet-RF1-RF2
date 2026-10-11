import io
from datetime import date, datetime

import pytest
from openpyxl import Workbook

from app.imports.parsing import FileFormatError, parse_commercial, parse_echus, read_table
from app.imports.spec import COMMERCIAL_HEADERS, ECHUS_HEADERS
from tests.builders import commercial_row, csv_bytes

H = COMMERCIAL_HEADERS


def messages(issues) -> str:
    return " | ".join(i.message for i in issues)


# --- Réalisés commerciaux -------------------------------------------------------------------


def test_fichier_valide() -> None:
    result = parse_commercial([H, commercial_row(), commercial_row(Mois="01/08/2026")])
    assert result.ok, messages(result.errors)
    assert result.warnings == []
    assert result.months == [date(2026, 7, 1), date(2026, 8, 1)]
    assert len(result.records) == 2 * 31
    assert result.rows_kept == 2


def test_colonne_manquante_bloque() -> None:
    header = [h for h in H if h != "Ventes_Fit"]
    result = parse_commercial([header])
    assert "Colonne Ventes_Fit introuvable (ligne 1)." in messages(result.errors)


def test_colonne_mal_orthographiee_suggestion() -> None:
    header = ["Ventes_fit" if h == "Ventes_Fit" else h for h in H]
    result = parse_commercial([header, commercial_row()])
    assert 'Colonne proche trouvée : "Ventes_fit"' in messages(result.errors)


def test_colonnes_de_cumul_ignorees() -> None:
    header = H + ["Cumul gross adds PREMIUM", "Cumul gross adds total"]
    result = parse_commercial([header, commercial_row() + [1, 2]])
    assert result.ok, messages(result.errors)
    assert "2 colonnes de cumul ignorées" in messages(result.warnings)


def test_autres_pays_ignores() -> None:
    other = commercial_row(Pays="Gabon", Ville="LBV")
    result = parse_commercial([H, commercial_row(), other])
    assert result.ok
    assert result.rows_ignored == 1
    assert "1 ligne hors Côte d'Ivoire sera ignorée" in messages(result.warnings)


def test_pays_avec_accents_accepte() -> None:
    result = parse_commercial([H, commercial_row(Pays="Côte d'Ivoire")])
    assert result.ok, messages(result.errors)


def test_ville_mal_ecrite_bloque() -> None:
    result = parse_commercial([H, commercial_row(Ville="ABI")])
    assert "Ligne 2 : ville ABI inconnue. Seule ville acceptée : ABJ." in messages(result.errors)


def test_mois_sans_annee_bloque() -> None:
    result = parse_commercial([H, commercial_row(Mois="juillet")])
    assert 'mois "juillet" non reconnu' in messages(result.errors)


def test_formats_de_mois() -> None:
    serial = (date(2026, 9, 1) - date(1899, 12, 30)).days
    rows = [
        H,
        commercial_row(Mois=datetime(2026, 7, 15)),
        commercial_row(Mois="2026-08-01"),
        commercial_row(Mois=serial),
    ]
    result = parse_commercial(rows)
    assert result.ok, messages(result.errors)
    assert result.months == [date(2026, 7, 1), date(2026, 8, 1), date(2026, 9, 1)]


def test_texte_dans_colonne_numerique() -> None:
    result = parse_commercial([H, commercial_row(Activations="n/a")])
    assert 'Ligne 2, colonne Activations : "n/a" n\'est pas un nombre.' in messages(result.errors)


def test_formule_refusee() -> None:
    result = parse_commercial([H, commercial_row(Activations="=A1+B1")])
    assert "formule" in messages(result.errors)


def test_formats_de_nombres() -> None:
    result = parse_commercial([H, commercial_row(Activations="1 030", Nb_echus="12,5")])
    assert result.ok, messages(result.errors)
    values = {r.metric: r.value for r in result.records}
    assert values["Activations"] == 1030
    assert values["Nb_echus"] == 12.5


def test_cellule_vide_vaut_zero() -> None:
    result = parse_commercial([H, commercial_row(Activations="")])
    assert {r.metric: r.value for r in result.records}["Activations"] == 0


def test_doublon_de_mois() -> None:
    result = parse_commercial([H, commercial_row(), commercial_row()])
    assert "ABJ / 01/07/2026 apparaît deux fois (lignes 2 et 3)." in messages(result.errors)


def test_total_incoherent_avertit() -> None:
    result = parse_commercial([H, commercial_row(Vente_total=1028)])
    assert result.ok
    assert "Vente_total 1 028, somme des offres 1 030." in messages(result.warnings)


def test_variation_par_rapport_au_mois_precedent_en_base() -> None:
    previous = {
        "Vente_total": {date(2026, 6, 1): 1030.0},
        "Parc_actif_total": {date(2026, 6, 1): 39000.0},
    }
    result = parse_commercial([H, commercial_row()], previous=previous)
    text = messages(result.warnings)
    assert "Parc_actif_total ABJ : -35 % en juillet 2026" in text
    assert "Vente_total" not in text


def test_mois_deja_importe() -> None:
    result = parse_commercial([H, commercial_row()], existing_months={date(2026, 7, 1)})
    assert "juillet 2026 est déjà présent" in messages(result.warnings)


def test_mois_manquant() -> None:
    result = parse_commercial([H, commercial_row(), commercial_row(Mois="01/09/2026")])
    assert "Aucune ligne pour août 2026." in messages(result.warnings)


def test_mois_manquant_depuis_le_dernier_import() -> None:
    existing = {date(2026, 5, 1)}
    result = parse_commercial([H, commercial_row()], existing_months=existing)
    assert "Aucune ligne pour juin 2026." in messages(result.warnings)


# --- Échus ------------------------------------------------------------------------------------


def test_echus_format_long() -> None:
    rows = [
        ECHUS_HEADERS,
        ["ABJ", "01/01/2025", 1, "5 345"],
        ["ABJ", "01/01/2025", 2, 4000],
        ["ABJ", "01/02/2025", 1, 5800],
    ]
    result = parse_echus(rows)
    assert result.ok, messages(result.errors)
    assert len(result.records) == 3
    assert result.records[0].value == 5345
    assert result.months == [date(2025, 1, 1), date(2025, 2, 1)]


@pytest.mark.parametrize("seniority", [0, 41, "a", 1.5])
def test_echus_anciennete_invalide(seniority: object) -> None:
    result = parse_echus([ECHUS_HEADERS, ["ABJ", "01/01/2025", seniority, 10]])
    assert "ancienneté" in messages(result.errors)


def test_echus_doublon() -> None:
    rows = [ECHUS_HEADERS, ["ABJ", "01/01/2025", 1, 10], ["ABJ", "01/01/2025", 1, 12]]
    result = parse_echus(rows)
    assert "ancienneté 1 apparaît deux fois (lignes 2 et 3)" in messages(result.errors)


def test_echus_ligne_total_ignoree_sans_avertissement() -> None:
    rows = [ECHUS_HEADERS, ["Total", "01/01/2025", 1, 99], ["ABJ", "01/01/2025", 1, 10]]
    result = parse_echus(rows)
    assert result.ok
    assert result.warnings == []
    assert len(result.records) == 1


CROSSTAB = [
    ["Anc.", "Villes", "janvier", "février"],
    [1, "Total", 37845, 63359],
    [1, "ABJ", 5345, 7595],
    [1, "LBV", 4621, 6929],
    [2, "ABJ", 100, None],
]


def test_echus_format_croise_sans_annee_bloque() -> None:
    result = parse_echus(CROSSTAB)
    assert "Format croisé détecté" in messages(result.errors)


def test_echus_format_croise_converti() -> None:
    result = parse_echus(CROSSTAB, year=2025)
    assert result.ok, messages(result.errors)
    values = {(r.month, r.seniority): r.value for r in result.records}
    assert values == {
        (date(2025, 1, 1), 1): 5345,
        (date(2025, 2, 1), 1): 7595,
        (date(2025, 1, 1), 2): 100,
    }
    text = messages(result.warnings)
    assert "année 2025 appliquée" in text
    assert "1 ligne d'autres villes sera ignorée" in text


def test_echus_ville_mal_ecrite_bloque() -> None:
    result = parse_echus([ECHUS_HEADERS, ["AJB", "01/01/2025", 1, 10]])
    assert "ville AJB inconnue" in messages(result.errors)


# --- Lecture des fichiers ---------------------------------------------------------------------


def test_csv_point_virgule_avec_bom() -> None:
    content = "\ufeff".encode() + csv_bytes([ECHUS_HEADERS, ["ABJ", "01/01/2025", 1, "5 345"]])
    rows = read_table(content, "echus.csv")
    assert rows[0] == ECHUS_HEADERS
    assert parse_echus(rows).ok


def test_csv_virgule() -> None:
    content = csv_bytes([ECHUS_HEADERS, ["ABJ", "01/01/2025", 1, 10]], sep=",")
    assert read_table(content, "echus.csv")[0] == ECHUS_HEADERS


def test_csv_windows_1252() -> None:
    row = commercial_row(Pays="Côte d'Ivoire")
    content = "\n".join(";".join(str(c) for c in r) for r in [H, row]).encode("cp1252")
    assert parse_commercial(read_table(content, "realises.csv")).ok


def xlsx_bytes(rows: list[list[object]], extra_sheet: bool = False) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    for row in rows:
        sheet.append(row)
    if extra_sheet:
        workbook.create_sheet("Autre")
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_xlsx_avec_date_et_formule() -> None:
    content = xlsx_bytes([ECHUS_HEADERS, ["ABJ", datetime(2025, 1, 1), 1, "=1+1"]])
    result = parse_echus(read_table(content, "echus.xlsx"))
    assert "formule" in messages(result.errors)


def test_xlsx_valide() -> None:
    content = xlsx_bytes([ECHUS_HEADERS, ["ABJ", datetime(2025, 1, 1), 1, 10]])
    assert parse_echus(read_table(content, "echus.xlsx")).ok


def test_xlsx_plusieurs_feuilles_refuse() -> None:
    content = xlsx_bytes([ECHUS_HEADERS], extra_sheet=True)
    with pytest.raises(FileFormatError, match="2 feuilles"):
        read_table(content, "echus.xlsx")


def test_format_inconnu() -> None:
    with pytest.raises(FileFormatError, match="Format non reconnu"):
        read_table(b"%PDF", "echus.pdf")
