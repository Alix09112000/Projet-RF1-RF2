"""Données de référence et compte administrateur. Sans effet si elles existent déjà.

Usage : python -m app.seed
"""

import os

from sqlalchemy import select

from app.auth.security import hash_password
from app.db import SessionLocal
from app.models import City, ForecastVersion, Role, Segment, User, VersionStatus

CITIES = [("ABJ", "Abidjan", "Côte d'Ivoire", "XOF")]
SEGMENTS = [("B2C", "Particuliers"), ("SME", "Entreprises"), ("DROPE", "DROPE")]
VERSIONS = [
    ("BI26", "Budget initial 2026", VersionStatus.published),
    ("RF1", "Reforecast 1 — 2026", VersionStatus.published),
    ("RF2", "Reforecast 2 — 2026", VersionStatus.draft),
]


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
