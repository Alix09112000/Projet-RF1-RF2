"""Axe du temps du modèle : 24 colonnes mensuelles, indépendantes de l'année (règle 1).

Colonnes Excel I à AF :
  I–N  : 6 mois réels      → slots 0 à 5
  O–T  : 6 mois RF2        → slots 6 à 11
  U–AF : 12 mois de BI     → slots 12 à 23
"""

from dataclasses import dataclass

SLOTS = 24
ACTUAL = range(0, 6)
RF2 = range(6, 12)
BI = range(12, 24)
FIRST_COLUMN = 9  # I
FCFA_PER_EUR = 655.957


@dataclass(frozen=True)
class Slot:
    index: int
    column: str
    period: str  # actual · rf2 · bi
    label: str


def column_letter(number: int) -> str:
    letters = ""
    while number:
        number, rest = divmod(number - 1, 26)
        letters = chr(65 + rest) + letters
    return letters


def column_index(letter: str) -> int:
    number = 0
    for char in letter.upper():
        number = number * 26 + ord(char) - 64
    return number


def slot_of_column(letter: str) -> int:
    slot = column_index(letter) - FIRST_COLUMN
    if not 0 <= slot < SLOTS:
        raise ValueError(f"Colonne {letter} hors de l'axe I–AF")
    return slot


def period_of(slot: int) -> str:
    if slot in ACTUAL:
        return "actual"
    if slot in RF2:
        return "rf2"
    return "bi"


def slots() -> list[Slot]:
    out = []
    for i in range(SLOTS):
        period = period_of(i)
        if period == "actual":
            label = f"Réel M{i + 1}"
        elif period == "rf2":
            label = f"RF2 M{i - 5}"
        else:
            label = f"BI M{i - 11}"
        out.append(Slot(i, column_letter(FIRST_COLUMN + i), period, label))
    return out


def eur_to_fcfa(eur: float) -> float:
    return eur * FCFA_PER_EUR


def fcfa_to_eur(fcfa: float) -> float:
    return fcfa / FCFA_PER_EUR


def keur_to_fcfa(keur: float) -> float:
    return keur * 1000 * FCFA_PER_EUR
