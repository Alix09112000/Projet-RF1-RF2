from app.imports.spec import COMMERCIAL_HEADERS

BASE: dict[str, object] = {
    "Pays": "Cote d Ivoire",
    "Ville": "ABJ",
    "Mois": "01/07/2026",
    "Ventes_premium": 300,
    "Ventes_Start": 500,
    "Ventes_Fit": 230,
    "Vente_total": 1030,
    "Parc equipe_total": 30000,
    "Parc actif_premium": 8000,
    "Parc_actif_start": 12000,
    "Parc_actif_fit": 5400,
    "Parc_actif_total": 25400,
    "Parc_actif_moyen_premium": 7900,
    "Parc_actif_moyen_start": 11900,
    "Parc_actif_moyen_fit": 5300,
    "Parc actif_moyen": 25100,
}


def commercial_row(values: dict[str, object] | None = None, **kw: object) -> list[object]:
    """Une ligne cohérente (totaux = somme des offres) ; 100 pour les autres colonnes."""
    data = {**BASE, **(values or {}), **kw}
    return [data.get(h, 100) for h in COMMERCIAL_HEADERS]


def csv_bytes(rows: list[list[object]], sep: str = ";") -> bytes:
    lines = (sep.join("" if c is None else str(c) for c in row) for row in rows)
    return "\n".join(lines).encode("utf-8")
