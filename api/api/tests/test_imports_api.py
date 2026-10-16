import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.imports.spec import COMMERCIAL_HEADERS, ECHUS_HEADERS
from app.models import ActualValue, Role
from tests.builders import commercial_row, csv_bytes
from tests.conftest import login
from tests.test_parsing import CROSSTAB

TWO_MONTHS = [COMMERCIAL_HEADERS, commercial_row(), commercial_row(Mois="01/08/2026")]


@pytest.fixture()
def controller(client: TestClient, make_user) -> None:
    make_user(Role.controller)
    login(client, "controller@test.ci")


def upload(client: TestClient, kind: str, rows, filename: str = "fichier.csv", year=None):
    data = {"year": str(year)} if year else {}
    files = {"file": (filename, csv_bytes(rows), "text/csv")}
    return client.post(f"/api/imports/{kind}/preview", files=files, data=data)


def confirm(client: TestClient, batch_id: int, ack: bool = False):
    return client.post(f"/api/imports/{batch_id}/confirm", json={"confirm_warnings": ack})


def count(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(ActualValue)) or 0


def test_verifier_puis_importer(client: TestClient, db: Session, controller) -> None:
    response = upload(client, "commercial", TWO_MONTHS)
    assert response.status_code == 200, response.text
    batch = response.json()
    assert batch["status"] == "pending"
    assert batch["errors"] == [] and batch["warnings"] == []
    assert batch["months"] == ["2026-07-01", "2026-08-01"]
    assert count(db) == 0  # rien n'est enregistré avant confirmation

    response = confirm(client, batch["id"])
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "accepted"
    assert count(db) == 62

    history = client.get("/api/imports").json()
    assert [b["status"] for b in history] == ["accepted"]
    sources = client.get("/api/imports/status").json()
    assert sources["commercial"]["last_month"] == "2026-08-01"
    assert sources["echus"]["last_month"] is None


def test_fichier_refuse_ne_peut_pas_etre_importe(client: TestClient, controller) -> None:
    header = [h for h in COMMERCIAL_HEADERS if h != "Activations"]
    batch = upload(client, "commercial", [header]).json()
    assert batch["status"] == "rejected"
    assert "Activations" in batch["errors"][0]["message"]
    assert confirm(client, batch["id"]).status_code == 409


def test_format_inconnu_refuse(client: TestClient, controller) -> None:
    batch = upload(client, "commercial", [["x"]], filename="realises.pdf").json()
    assert batch["status"] == "rejected"
    assert "Format non reconnu" in batch["errors"][0]["message"]


def test_avertissements_a_confirmer(client: TestClient, controller) -> None:
    rows = [COMMERCIAL_HEADERS, commercial_row(Vente_total=1028)]
    batch = upload(client, "commercial", rows).json()
    assert batch["status"] == "pending"
    assert len(batch["warnings"]) == 1
    assert confirm(client, batch["id"], ack=False).status_code == 400
    response = confirm(client, batch["id"], ack=True)
    assert response.status_code == 200
    assert response.json()["warnings_confirmed"] is True


def test_reimport_remplace_le_mois(client: TestClient, db: Session, controller) -> None:
    first = upload(client, "commercial", [COMMERCIAL_HEADERS, commercial_row()]).json()
    confirm(client, first["id"])

    rows = [COMMERCIAL_HEADERS, commercial_row(Activations=999)]
    second = upload(client, "commercial", rows).json()
    assert "déjà présent" in second["warnings"][0]["message"]
    assert confirm(client, second["id"], ack=True).status_code == 200

    assert count(db) == 31
    value = db.scalar(select(ActualValue.value).where(ActualValue.metric == "Activations"))
    assert value == 999


def test_annulation(client: TestClient, db: Session, controller) -> None:
    batch = upload(client, "commercial", TWO_MONTHS).json()
    response = client.post(f"/api/imports/{batch['id']}/cancel")
    assert response.json()["status"] == "cancelled"
    assert confirm(client, batch["id"]).status_code == 409
    assert count(db) == 0


def test_echus_format_croise_avec_annee(client: TestClient, controller) -> None:
    without_year = upload(client, "echus", CROSSTAB).json()
    assert without_year["status"] == "rejected"
    assert "Format croisé" in without_year["errors"][0]["message"]

    with_year = upload(client, "echus", CROSSTAB, year=2025).json()
    assert with_year["status"] == "pending"
    assert with_year["months"] == ["2025-01-01", "2025-02-01"]


def test_fichier_original_conserve(client: TestClient, controller) -> None:
    batch = upload(client, "commercial", TWO_MONTHS).json()
    response = client.get(f"/api/imports/{batch['id']}/file")
    assert response.status_code == 200
    assert response.content == csv_bytes(TWO_MONTHS)


def test_modeles_vides(client: TestClient, controller) -> None:
    commercial = client.get("/api/imports/templates/commercial")
    assert commercial.status_code == 200
    assert "text/csv" in commercial.headers["content-type"]
    assert "Parc equipe_total" in commercial.text
    echus = client.get("/api/imports/templates/echus")
    assert ";".join(ECHUS_HEADERS) in echus.text


def test_contributeur_refuse(client: TestClient, make_user) -> None:
    make_user(Role.contributor)
    login(client, "contributor@test.ci")
    assert upload(client, "commercial", TWO_MONTHS).status_code == 403
    assert client.get("/api/imports").status_code == 403


def test_type_de_fichier_inconnu(client: TestClient, controller) -> None:
    assert upload(client, "budget", TWO_MONTHS).status_code == 422
