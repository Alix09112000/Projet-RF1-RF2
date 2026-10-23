import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AssumptionChange, ForecastVersion, ListEntry, Role, VersionStatus
from app.seed import LIST_ENTRIES
from tests.conftest import login
from tests.fictif_drcom import B2C1_CELLS


@pytest.fixture()
def versions(db: Session) -> None:
    db.add_all(
        [
            ForecastVersion(code="RF1", label="RF1", status=VersionStatus.published),
            ForecastVersion(code="RF2", label="RF2", status=VersionStatus.draft),
        ]
    )
    db.add_all(ListEntry(entity=e, country=c, city=v, source_row=r) for r, e, c, v in LIST_ENTRIES)
    db.commit()


@pytest.fixture()
def drcom(client: TestClient, db: Session, make_user, versions) -> None:
    user = make_user(Role.contributor, email="drcom@test.ci")
    user.direction = "DRCOM"
    db.commit()
    login(client, "drcom@test.ci")


def save(client: TestClient, cells, comment=None, version="RF2", module="B2C1"):
    return client.put(f"/api/inputs/{version}/{module}", json={"cells": cells, "comment": comment})


def test_lecture_du_module(client: TestClient, drcom) -> None:
    data = client.get("/api/inputs/RF2/B2C1").json()
    assert data["editable"] is True
    assert len(data["slots"]) == 24
    assert len(data["lines"]) == 70
    first = data["lines"][0]
    assert first["row"] == 9 and first["values"] == [None] * 24
    assert {b["row"] for b in data["balances"]} == {30, 225, 396}


def test_saisie_du_jeu_fictif_et_soldes(client: TestClient, drcom) -> None:
    response = save(client, B2C1_CELLS, comment="Jeu fictif")
    assert response.status_code == 200, response.text
    assert response.json()["changed"] == 1334
    data = client.get("/api/inputs/RF2/B2C1").json()
    start = next(b for b in data["balances"] if b["row"] == 30)
    assert start["values"][6] == pytest.approx(0.5)
    assert data["warnings"] == []


def test_historique_ancienne_et_nouvelle_valeur(client: TestClient, db: Session, drcom) -> None:
    save(client, [{"row": 329, "slot": 6, "value": 15}])
    save(client, [{"row": 329, "slot": 6, "value": 16}], comment="Hausse tarifaire")
    save(client, [{"row": 329, "slot": 6, "value": 16}])  # inchangé : pas d'historique
    history = client.get("/api/inputs/RF2/B2C1/history?row=329").json()
    assert [(h["old_value"], h["new_value"]) for h in history] == [(15, 16), (None, 15)]
    assert history[0]["comment"] == "Hausse tarifaire"
    assert history[0]["label"] == "Prix abonnement PREMIUM (HT)"
    save(client, [{"row": 329, "slot": 6, "value": None}])
    lines = client.get("/api/inputs/RF2/B2C1").json()["lines"]
    assert next(x for x in lines if x["row"] == 329)["values"][6] is None
    assert db.scalar(select(func.count()).select_from(AssumptionChange)) == 3


def test_ligne_non_saisissable(client: TestClient, drcom) -> None:
    response = save(client, [{"row": 30, "slot": 6, "value": 0.5}])
    assert response.status_code == 422
    assert "pas une cellule de saisie" in response.json()["detail"][0]


def test_mois_reel_non_saisissable(client: TestClient, drcom) -> None:
    response = save(client, [{"row": 15, "slot": 2, "value": 100}])
    assert response.status_code == 422
    assert "à partir de la colonne O" in response.json()["detail"][0]


def test_version_figee(client: TestClient, drcom) -> None:
    response = save(client, [{"row": 15, "slot": 6, "value": 100}], version="RF1")
    assert response.status_code == 409
    assert client.get("/api/inputs/RF1/B2C1").json()["editable"] is False


def test_autre_direction_refusee(client: TestClient, db: Session, make_user, versions) -> None:
    user = make_user(Role.contributor, email="drope@test.ci")
    user.direction = "DROPE"
    db.commit()
    login(client, "drope@test.ci")
    assert client.get("/api/inputs/RF2/SME1").json()["editable"] is False
    response = save(client, [{"row": 11, "slot": 6, "value": 10}], module="SME1")
    assert response.status_code == 403


def test_consultation_refusee(client: TestClient, make_user, versions) -> None:
    make_user(Role.viewer)
    login(client, "viewer@test.ci")
    assert save(client, [{"row": 15, "slot": 6, "value": 1}]).status_code == 403


def test_module_inconnu(client: TestClient, drcom) -> None:
    assert client.get("/api/inputs/RF2/KPI").status_code == 404


def test_parametres_de_la_ville(client: TestClient, make_user, versions) -> None:
    make_user(Role.controller)
    login(client, "controller@test.ci")
    data = client.get("/api/parameters").json()
    assert len(data["choices"]) == 14
    ok = client.put("/api/parameters", json={"legal_entity": "GVA CIV", "city": "Abidjan"})
    assert ok.status_code == 200
    assert ok.json()["values"] == {"legal_entity": "GVA CIV", "city": "Abidjan"}
    bad = client.put("/api/parameters", json={"legal_entity": "GVA CIV", "city": "Kigali"})
    assert bad.status_code == 422


def test_parametres_reserves(client: TestClient, drcom) -> None:
    response = client.put("/api/parameters", json={"legal_entity": "GVA CIV", "city": "Abidjan"})
    assert response.status_code == 403


def test_mix_hors_de_0_a_100_refuse(client: TestClient, db: Session, drcom) -> None:
    refused = save(client, [{"row": 29, "slot": 6, "value": 1.4}])
    assert refused.status_code == 422
    assert "entre 0 % et 100 %" in str(refused.json())
    assert "140 %" in str(refused.json())
    negative = save(client, [{"row": 31, "slot": 6, "value": -0.1}])
    assert negative.status_code == 422
    # Rien n'est enregistré quand une cellule est refusée.
    assert client.get("/api/inputs/RF2/B2C1").json()["lines"][3]["values"][6] is None
    assert db.scalar(select(func.count()).select_from(AssumptionChange)) == 0


def test_mix_aux_bornes_accepte(client: TestClient, drcom) -> None:
    assert (
        save(
            client, [{"row": 29, "slot": 6, "value": 1.0}, {"row": 31, "slot": 6, "value": 0.0}]
        ).status_code
        == 200
    )


def test_mois_reels_suivent_le_mois_de_reference(client: TestClient, db: Session, drcom) -> None:
    """En août, janvier à juillet sont réels ; en juillet, janvier à juin."""
    from app.models import CityParameter

    data = client.get("/api/inputs/RF2/B2C1").json()
    assert data["real_months"] == 6
    assert [s["period"] for s in data["slots"]].count("actual") == 6

    db.scalar(select(CityParameter).where(CityParameter.key == "reference_month")).value = "2026-08"
    db.commit()
    data = client.get("/api/inputs/RF2/B2C1").json()
    assert data["real_months"] == 7
    periods = [s["period"] for s in data["slots"]]
    assert periods[:7] == ["actual"] * 7 and periods[7] == "rf2" and periods[12] == "bi"
    assert data["slots"][7]["label"] == "RF2 M1"
    # Un mois réel (juillet, slot 6) n'est plus saisissable sur une ligne de prévision.
    forecast_line = next(line for line in data["lines"] if line["first_slot"] == 7)
    response = save(client, [{"row": forecast_line["row"], "slot": 6, "value": 1}])
    assert response.status_code == 422


def test_parametre_mois_de_reference(client: TestClient, db: Session, make_user, versions) -> None:
    make_user(Role.controller, email="cg@test.ci")
    login(client, "cg@test.ci")
    pair = {"legal_entity": LIST_ENTRIES[0][1], "city": LIST_ENTRIES[0][3]}
    assert client.get("/api/parameters").json()["reference_month"] == "2026-07"
    ok = client.put("/api/parameters", json={**pair, "reference_month": "2026-08"})
    assert ok.status_code == 200 and ok.json()["reference_month"] == "2026-08"
    bad = client.put("/api/parameters", json={**pair, "reference_month": "2026-13"})
    assert bad.status_code == 422
