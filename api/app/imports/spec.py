"""Structure attendue des fichiers déposés (voir « Format des fichiers d'import »)."""

CITY = "ABJ"
COUNTRY_KEY = "cote d ivoire"  # « Cote d Ivoire » normalisé (accents et apostrophes retirés)
MAX_SENIORITY = 40
VARIATION_THRESHOLD = 0.30

# Fichier 1 — Réalisés commerciaux : colonnes A à AH de l'onglet « Source BR PBI ».
# Les en-têtes sont repris tels quels, irrégularités comprises.
COMMERCIAL_HEADERS = [
    "Pays",
    "Ville",
    "Mois",
    "Ventes_premium",
    "Ventes_Start",
    "Ventes_Fit",
    "Vente_total",
    "Parc equipe_total",
    "Parc actif_premium",
    "Parc_actif_start",
    "Parc_actif_fit",
    "Parc_actif_total",
    "Parc_actif_moyen_premium",
    "Parc_actif_moyen_start",
    "Parc_actif_moyen_fit",
    "Parc actif_moyen",
    "Retour_echus_total",
    "Reabo_1er_ech",
    "Reabo_repeteur",
    "Reabo_echus_m_1",
    "Reabo_parmi_aae",
    "Reabo_av_ech",
    "AAE_1er_ech",
    "AAE_repeteur",
    "AAE_retour_echus_m_1",
    "AAE_total",
    "Nb_echus",
    "Activations",
    "Reabonnement_mobile_money",
    "Reabonnement_distributeurs",
    "Reabonnement Shop_in_shop",
    "Reabonnement_espace_client",
    "NB_RECO_APRES_DEMENAGEMENT",
    "NB_DEMENAGEMENT",
]
COMMERCIAL_METRICS = COMMERCIAL_HEADERS[3:]

# Total attendu = somme des trois offres (avertissement si écart).
TOTAL_CHECKS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Vente_total", ("Ventes_premium", "Ventes_Start", "Ventes_Fit")),
    ("Parc_actif_total", ("Parc actif_premium", "Parc_actif_start", "Parc_actif_fit")),
    (
        "Parc actif_moyen",
        ("Parc_actif_moyen_premium", "Parc_actif_moyen_start", "Parc_actif_moyen_fit"),
    ),
)
VARIATION_METRICS = ("Vente_total", "Parc_actif_total")

# Fichier 2 — Échus : une ligne par mois et par ancienneté.
ECHUS_HEADERS = ["Ville", "Mois", "Anciennete_mois", "Nb_echus"]
ECHUS_SERIES = "Nb_echus (total du mois)"

TEMPLATES = {
    "commercial": ("Modele_Realises_commerciaux.csv", COMMERCIAL_HEADERS),
    "echus": ("Modele_Echus.csv", ECHUS_HEADERS),
}
