"""Données de référence et compte administrateur. Sans effet si elles existent déjà.

Usage : python -m app.seed
"""

import os

from sqlalchemy import select

from app.auth.security import hash_password
from app.db import SessionLocal
from app.models import (
    City,
    CityParameter,
    ForecastVersion,
    ListEntry,
    Role,
    Segment,
    User,
    VersionStatus,
)

CITIES = [("ABJ", "Abidjan", "Côte d'Ivoire", "XOF")]
SEGMENTS = [("B2C", "Particuliers"), ("SME", "Entreprises"), ("DROPE", "DROPE")]
VERSIONS = [
    ("BI26", "Budget initial 2026", VersionStatus.published),
    ("RF1", "Reforecast 1 — 2026", VersionStatus.published),
    ("RF2", "Reforecast 2 — 2026", VersionStatus.draft),
]

# Table List du modèle (lignes 2 à 15) : entité légale / pays / ville.
LIST_ENTRIES = [
    (2, "GVA SAS", "France", "Paris"),
    (3, "GVA Gabon", "Gabon", "Libreville"),
    (4, "GVA Togo", "Togo", "Lomé"),
    (5, "GVA Congo", "Congo", "Pointe-Noire"),
    (6, "GVA CIV", "CIV", "Abidjan"),
    (7, "GVA Rwanda", "Rwanda", "Kigali"),
    (8, "GVA Congo", "Congo", "Brazzaville"),
    (9, "GVA BF", "BF", "Ouagadougou"),
    (10, "GVA RDC", "RDC", "Kinshasa"),
    (11, "GVA Rwanda", "Rwanda", "Rubavu"),
    (12, "GVA RDC", "RDC", "Goma"),
    (13, "GVA Gabon", "Gabon", "Port-Gentil"),
    (14, "GVA BF", "BF", "Bobo Dioulasso"),
    (15, "GVA Uganda", "Uganda", "Kampala"),
]
DEFAULT_PARAMETERS = {"legal_entity": "GVA CIV", "city": "Abidjan"}


def run() -> None:
    with SessionLocal() as db:
        for code, name, country, currency in CITIES:
            if db.scalar(select(City).where(City.code == code)) is None:
                db.add(City(code=code, name=name, country=country, currency=currency))

        for code, name in SEGMENTS:
            if db.scalar(select(Segment).where(Segment.code == code)) is None:
                db.add(Segment(code=code, name=name))

        for code, label, status in VERSIONS:
            if db.scalar(select(ForecastVersion).where(ForecastVersion.code == code)) is None:
                db.add(ForecastVersion(code=code, label=label, status=status))

        for row, entity, country, city in LIST_ENTRIES:
            exists = db.scalar(
                select(ListEntry).where(ListEntry.entity == entity, ListEntry.city == city)
            )
            if exists is None:
                db.add(ListEntry(entity=entity, country=country, city=city, source_row=row))

        for key, value in DEFAULT_PARAMETERS.items():
            if db.scalar(select(CityParameter).where(CityParameter.key == key)) is None:
                db.add(CityParameter(key=key, value=value))

        has_admin = db.scalar(select(User).where(User.role == Role.admin)) is not None
        email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
        password = os.environ.get("ADMIN_PASSWORD", "")
        if not has_admin:
            if email and len(password) >= 10:
                db.add(
                    User(
                        email=email,
                        full_name=os.environ.get("ADMIN_NAME", "Administrateur"),
                        password_hash=hash_password(password),
                        role=Role.admin,
                    )
                )
                print(f"Compte administrateur créé : {email}")
            else:
                print(
                    "Aucun administrateur. Définir ADMIN_EMAIL et ADMIN_PASSWORD "
                    "(10 caractères minimum) puis relancer : python -m app.seed"
                )

        db.commit()
    print("Données de référence à jour.")


if __name__ == "__main__":
    run()
