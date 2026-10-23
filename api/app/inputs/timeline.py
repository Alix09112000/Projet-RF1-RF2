"""Axe du temps du modèle : 24 colonnes mensuelles, indépendantes de l'année (règle 1).

Colonnes Excel I à AF :
  I–N  : mois réels        → slots 0 à n−1 (6 par défaut)
  O–T  : mois RF2          → slots n à 11 (le reste de l'exercice)
  U–AF : 12 mois de BI     → slots 12 à 23

Le nombre de mois réels n dépend du mois de référence : le mois précédent est le dernier réel
(en août : janvier à juillet = 7 mois réels). L'exercice commence en janvier.
"""

from dataclasses import dataclass
from datetime import date

SLOTS = 24
DEFAULT_REAL = 6
ACTUAL = range(0, DEFAULT_REAL)
RF2 = range(DEFAULT_REAL, 12)
BI = range(12, 24)
YEAR = 12
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


def real_months(reference: date) -> int:
    """Nombre de mois réels pour un mois de référence : janvier → mois précédent (0 à 11)."""
    return reference.month - 1


def period_of(slot: int, n_real: int = DEFAULT_REAL) -> str:
    if slot < n_real:
        return "actual"
    if slot < YEAR:
        return "rf2"
    return "bi"


def slots(n_real: int = DEFAULT_REAL) -> list[Slot]:
    out = []
    for i in range(SLOTS):
        period = period_of(i, n_real)
        if period == "actual":
            label = f"Réel M{i + 1}"
        elif period == "rf2":
            label = f"RF2 M{i - n_real + 1}"
        else:
            label = f"BI M{i - YEAR + 1}"
        out.append(Slot(i, column_letter(FIRST_COLUMN + i), period, label))
    return out


def eur_to_fcfa(eur: float) -> float:
    return eur * FCFA_PER_EUR


def fcfa_to_eur(fcfa: float) -> float:
    return fcfa / FCFA_PER_EUR


def keur_to_fcfa(keur: float) -> float:
    return keur * 1000 * FCFA_PER_EUR
