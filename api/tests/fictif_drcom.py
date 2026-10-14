"""Jeu fictif DRCOM : valeurs inventées, au format du modèle. Aucune donnée Canalbox."""

from app.inputs.catalog import B2C1, SME1, Module

SHARES = {
    "B2C1": {29: 0.30, 31: 0.20, 224: 0.35, 226: 0.15},
    "SME1": {17: 0.40, 19: 0.10, 20: 0.05, 186: 0.40, 188: 0.10, 189: 0.05},
}


def fictive_cells(module: Module) -> list[dict[str, float | int]]:
    """Une valeur plausible par cellule saisissable, déterministe."""
    cells: list[dict[str, float | int]] = []
    shares = SHARES[module.code]
    for line in module.lines:
        for slot in line.editable_slots:
            if line.row in shares:
                value: float = shares[line.row]
            elif line.unit == "%":
                value = 0.05
            elif line.unit == "EUR":
                value = 15.0 + line.row % 7
            else:
                value = float(100 + line.row + slot)
            cells.append({"row": line.row, "slot": slot, "value": value})
    return cells


B2C1_CELLS = fictive_cells(B2C1)
SME1_CELLS = fictive_cells(SME1)
