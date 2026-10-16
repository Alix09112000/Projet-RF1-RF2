"""Cellules beiges (saisie) de B2C1 et SME1, reprises des fiches « Fiche_onglet_B2C1 » et
« Fiche_onglet_SME1 » (feuille « Lignes à saisir »). Rien n'est ajouté qui n'y figure pas.

Chaque ligne : (ligne Excel, libellé, unité, nature, première colonne saisie, rubrique).
Nature : ENTRÉE (toute la ligne est saisie) ou MIXTE (saisie sur les colonnes indiquées,
calcul ailleurs). Première colonne : I (réel + RF2 + BI), N (dernier réel + RF2 + BI)
ou O (RF2 + BI).
"""

from dataclasses import dataclass, field

from app.inputs.timeline import SLOTS, slot_of_column


@dataclass(frozen=True)
class InputLine:
    row: int
    label: str
    unit: str
    nature: str
    first_column: str
    section: str
    note: str = ""

    @property
    def first_slot(self) -> int:
        return slot_of_column(self.first_column)

    @property
    def editable_slots(self) -> range:
        return range(self.first_slot, SLOTS)


@dataclass(frozen=True)
class Balance:
    """Ligne calculée comme solde : 1 − somme des lignes saisies."""

    row: int
    label: str
    parts: tuple[int, ...]
    confirmed: bool  # False : déduit des valeurs du modèle vide, à confirmer (voir questions)


@dataclass(frozen=True)
class Module:
    code: str
    name: str
    direction: str
    lines: tuple[InputLine, ...]
    balances: tuple[Balance, ...] = field(default=())

    def line(self, row: int) -> InputLine | None:
        return next((line for line in self.lines if line.row == row), None)


def _lines(rows: list[tuple[int, str, str, str, str, str]]) -> tuple[InputLine, ...]:
    return tuple(InputLine(*r) for r in rows)


E, M = "ENTRÉE", "MIXTE"
P = "%"

B2C1 = Module(
    code="B2C1",
    name="Particuliers (B2C)",
    direction="DRCOM",
    lines=_lines([
        (9, "Jours fériés / congés", "#", E, "I", "Calendrier"),
        (15, "Ventes brutes · Internal VAD D2D", "#", M, "O", "Ventes brutes"),
        (16, "Ventes brutes · Internal VAD SiS", "#", E, "O", "Ventes brutes"),
        (17, "Ventes brutes · External VAD D2D", "#", E, "O", "Ventes brutes"),
        (18, "Ventes brutes · Distribution Network", "#", E, "O", "Ventes brutes"),
        (29, "Mix ventes PREMIUM", P, M, "O", "Ventes brutes"),
        (31, "Mix ventes FIT", P, M, "O", "Ventes brutes"),
        (49, "Superviseurs · Internal RVADs D2D", "#", M, "I", "Productivité commerciale"),
        (50, "Superviseurs · Internal RVADs SiS", "#", E, "I", "Productivité commerciale"),
        (51, "Superviseurs · External RVADs D2D", "#", E, "I", "Productivité commerciale"),
        (59, "Vendeurs · Internal VADs D2D", "#", M, "I", "Productivité commerciale"),
        (60, "Vendeurs · Internal VADs SiS", "#", E, "I", "Productivité commerciale"),
        (61, "Vendeurs · External VADs D2D", "#", E, "I", "Productivité commerciale"),
        (70, "Points de vente actifs · réseau de distribution", "#", M, "I",
         "Productivité commerciale"),
        (89, "Demandes de relocalisation", "#", E, "O", "Base équipée"),
        (119, "Ajustement du parc actif", P, E, "I", "Base active"),
        (159, "% AAE premier échu", P, M, "O", "Renouvellement AAE"),
        (160, "% AAE autres échus", P, E, "O", "Renouvellement AAE"),
        (161, "% AAE échus M-1", P, M, "O", "Renouvellement AAE"),
        (170, "Taux de renouvellement premier échu", P, M, "O", "Renouvellement AAE"),
        (171, "Taux de renouvellement autres échus", P, M, "O", "Renouvellement AAE"),
        (172, "Taux de renouvellement échus M-1", P, E, "O", "Renouvellement AAE"),
        (176, "Mix renouvellement AAE PREMIUM", P, E, "O", "Renouvellement AAE"),
        (177, "Mix renouvellement AAE FIT", P, E, "O", "Renouvellement AAE"),
        *[(199 + i, f"Taux de winback échus M-{i + 1}", P, M, "O", "Winback") for i in range(7)],
        (224, "Mix winback PREMIUM", P, E, "I", "Winback"),
        (226, "Mix winback FIT", P, E, "I", "Winback"),
        (258, "Déprovisionnement manuel", "#", E, "O", "Suspendus"),
        (276, "GI · PREMIUM", "#", E, "O", "GI / personnel GVA"),
        (277, "GI · START", "#", E, "O", "GI / personnel GVA"),
        (278, "GI · FIT", "#", E, "O", "GI / personnel GVA"),
        (282, "Personnel GVA · PREMIUM", "#", E, "O", "GI / personnel GVA"),
        (283, "Personnel GVA · START", "#", E, "O", "GI / personnel GVA"),
        (284, "Personnel GVA · FIT", "#", E, "O", "GI / personnel GVA"),
        (310, "Remise / gestion abonnés", "kEUR", M, "O", "Revenus"),
        (329, "Prix abonnement PREMIUM (HT)", "EUR", E, "O", "Prix · abonnés"),
        (330, "Prix abonnement START (HT)", "EUR", E, "O", "Prix · abonnés"),
        (331, "Prix abonnement FIT (HT)", "EUR", E, "O", "Prix · abonnés"),
        (345, "Prix abonnement PREMIUM (HT)", "EUR", E, "O", "Prix · GI"),
        (346, "Prix abonnement START (HT)", "EUR", E, "O", "Prix · GI"),
        (347, "Prix abonnement FIT (HT)", "EUR", E, "O", "Prix · GI"),
        (360, "Prix abonnement PREMIUM (HT)", "EUR", E, "O", "Prix · personnel GVA"),
        (361, "Prix abonnement START (HT)", "EUR", E, "O", "Prix · personnel GVA"),
        (362, "Prix abonnement FIT (HT)", "EUR", E, "O", "Prix · personnel GVA"),
        (368, "Coupons · opération", "#", E, "I", "Coupons"),
        (371, "Winback de renouvellement additionnel (prévision)", "#", E, "N", "Coupons"),
        (372, "Coût d'un coupon", "EUR", E, "N", "Coupons"),
        (384, "FAS PREMIUM standard (HT)", "EUR", E, "O", "FAS"),
        (385, "FAS START standard (HT)", "EUR", E, "O", "FAS"),
        (386, "FAS FIT standard (HT)", "EUR", E, "O", "FAS"),
        (395, "Canal de renouvellement · Distributeurs", P, M, "O", "Canaux de renouvellement"),
        (397, "Canal de renouvellement · Espace Client", P, E, "O", "Canaux de renouvellement"),
        (398, "Canal de renouvellement · MoMo agrégateur 1", P, E, "O",
         "Canaux de renouvellement"),
        (399, "Canal de renouvellement · MoMo agrégateur 2", P, E, "O",
         "Canaux de renouvellement"),
        (400, "Canal de renouvellement · MoMo agrégateur 3", P, E, "O",
         "Canaux de renouvellement"),
        (414, "Frais · Distributeurs (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (415, "Frais · SiS + VAD (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (416, "Frais · Espace Client (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (417, "Frais · MoMo agrégateur 1 (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (418, "Frais · MoMo agrégateur 2 (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (419, "Frais · MoMo agrégateur 3 (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (434, "Coût par CPE", "EUR", E, "O", "Coût d'acquisition (SAC)"),
        (438, "Commission moyenne par vente · VAD externe", "EUR", E, "O",
         "Coût d'acquisition (SAC)"),
        (442, "Commission moyenne par vente · réseau de distribution", "EUR", E, "O",
         "Coût d'acquisition (SAC)"),
    ]),
    balances=(
        Balance(30, "Mix ventes START", (29, 31), True),
        Balance(225, "Mix winback START", (224, 226), True),
        Balance(396, "Canal de renouvellement · SiS + VAD", (395, 397, 398, 399, 400), False),
    ),
)

SME_OFFERS = ("Offer SME 50 Mbps", "Offer SME 200 Mbps", "OFFRE 3", "OFFRE 4")

SME1 = Module(
    code="SME1",
    name="Entreprises (SME)",
    direction="DRCOM",
    lines=_lines([
        (11, "Ventes brutes", "#", M, "O", "Ventes brutes"),
        (17, "Mix ventes Offer SME 50 Mbps", P, M, "O", "Ventes brutes"),
        (19, "Mix ventes OFFRE 3", P, M, "O", "Ventes brutes"),
        (20, "Mix ventes OFFRE 4", P, M, "O", "Ventes brutes"),
        (46, "Net adds / ventes brutes", P, E, "O", "Base équipée"),
        (49, "Nouveaux équipés issus des ventes du mois", P, E, "O", "Base équipée"),
        (82, "Ajustement du parc actif", P, E, "I", "Base active"),
        (122, "% AAE premier échu", P, M, "O", "Renouvellement AAE"),
        (123, "% AAE autres échus", P, M, "O", "Renouvellement AAE"),
        (131, "Taux de renouvellement premier échu", P, M, "O", "Renouvellement AAE"),
        (132, "Taux de renouvellement autres échus", P, M, "O", "Renouvellement AAE"),
        (135, "Mix renouvellement AAE Offer SME 50 Mbps", P, E, "O", "Renouvellement AAE"),
        (136, "Mix renouvellement AAE OFFRE 3", P, E, "O", "Renouvellement AAE"),
        (137, "Mix renouvellement AAE OFFRE 4", P, E, "O", "Renouvellement AAE"),
        *[(161 + i, f"Taux de winback échus M-{i + 1}", P, E, "O", "Winback") for i in range(6)],
        (186, "Mix winback Offer SME 50 Mbps", P, E, "I", "Winback"),
        (188, "Mix winback OFFRE 3", P, E, "I", "Winback"),
        (189, "Mix winback OFFRE 4", P, E, "I", "Winback"),
        (221, "Déprovisionnement manuel", "#", E, "O", "Suspendus"),
        (223, "Échus > 6 mois après déprovisionnement", "#", M, "O", "Suspendus"),
        *[(241 + i, f"GI · {o}", "#", E, "O", "GI / personnel GVA")
          for i, o in enumerate(SME_OFFERS)],
        *[(248 + i, f"Personnel GVA · {o}", "#", E, "O", "GI / personnel GVA")
          for i, o in enumerate(SME_OFFERS)],
        (261, "Relocalisations N-1", "#", E, "I", "Indicateurs"),
        (277, "Remise / gestion abonnés", "kEUR", E, "O", "Revenus"),
        *[(295 + i, f"Prix abonnement {o} (HT)", "EUR", E, "I", "Prix · abonnés")
          for i, o in enumerate(SME_OFFERS)],
        *[(313 + i, f"Prix abonnement {o} (HT)", "EUR", E, "I", "Prix · GI")
          for i, o in enumerate(SME_OFFERS)],
        *[(330 + i, f"Prix abonnement {o} (HT)", "EUR", E, "I", "Prix · personnel GVA")
          for i, o in enumerate(SME_OFFERS)],
        *[(346 + i, f"FAS {o} standard (HT)", "EUR", E, "I", "FAS")
          for i, o in enumerate(SME_OFFERS)],
        (357, "Canal de renouvellement · Distributeurs", P, M, "O", "Canaux de renouvellement"),
        (359, "Canal de renouvellement · Espace Client", P, E, "O", "Canaux de renouvellement"),
        (360, "Canal de renouvellement · MoMo agrégateur 1", P, E, "O",
         "Canaux de renouvellement"),
        (361, "Canal de renouvellement · MoMo agrégateur 2", P, E, "O",
         "Canaux de renouvellement"),
        (362, "Canal de renouvellement · MoMo agrégateur 3", P, E, "O",
         "Canaux de renouvellement"),
        (376, "Frais · Distributeurs (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (377, "Frais · SiS + VAD (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (378, "Frais · Espace Client (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (379, "Frais · MoMo agrégateur 1 (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (380, "Frais · MoMo agrégateur 2 (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (381, "Frais · MoMo agrégateur 3 (% du CA HT)", P, E, "O", "Frais de renouvellement"),
        (396, "Coût par CPE", "EUR", E, "O", "Coût d'acquisition (SAC)"),
    ]),
    balances=(
        Balance(18, "Mix ventes Offer SME 200 Mbps", (17, 19, 20), False),
        Balance(187, "Mix winback Offer SME 200 Mbps", (186, 188, 189), False),
        Balance(358, "Canal de renouvellement · SiS + VAD", (357, 359, 360, 361, 362), False),
    ),
)

# Notes reprises telles quelles des commentaires du modèle (colonne AK).
NOTES = {
    ("B2C1", 119): "Préciser ici la variation de parc actif moyen à intégrer.",
    ("B2C1", 258): "En cas de déprovisionnement nécessaire (anticipation d'OTB Full).",
    ("SME1", 82): "Préciser ici la variation de parc actif moyen à intégrer.",
    ("SME1", 49): "Attention à la valeur de départ du dernier mois.",
    ("SME1", 221): "En cas de déprovisionnement nécessaire (anticipation d'OTB Full).",
    ("SME1", 396): "À renseigner en négatif.",
    **{("SME1", r): "Prix de vente : ne pas jouer avec l'ARPU ici." for r in (295, 296, 297,
                                                                             313, 314, 330, 331)},
}

MODULES = {m.code: m for m in (B2C1, SME1)}


def note(module: str, row: int) -> str:
    return NOTES.get((module, row), "")
