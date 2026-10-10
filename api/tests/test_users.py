import pytest
from fastapi.testclient import TestClient

from app.models import Role
from tests.conftest import login

NEW_USER = {
    "email": "nouveau@test.ci",
    "full_name": "Nouveau Contributeur",
    "password": "un-mot-de-passe-long",
    "role": "contributor",
    "direction": "Direction Commerciale",
}


@pytest.mark.parametrize("role", [Role.contributor, Role.controller, Role.viewer])
def test_liste_reservee_a_admin(client: TestClient, make_user, role: Role) -> None:
    user = make_user(role)
    login(client, user.email)
    assert client.get("/api/users").status_code == 403
    assert client.post("/api/users", json=NEW_USER).status_code == 403


def test_admin_cree_un_compte_utilisable(client: TestClient, make_user) -> None:
    make_user(Role.admin)
    login(client, "admin@test.ci")

    response = client.post("/api/users", json=NEW_USER)
    assert response.status_code == 201
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    emails = [u["email"] for u in client.get("/api/users").json()]
    assert "nouveau@test.ci" in emails

    client.post("/api/auth/logout")
    login(client, "nouveau@test.ci", NEW_USER["password"])
    assert client.get("/api/auth/me").json()["direction"] == "Direction Commerciale"


def test_doublon_refuse(client: TestClient, make_user) -> None:
    make_user(Role.admin)
    login(client, "admin@test.ci")
    assert client.post("/api/users", json=NEW_USER).status_code == 201
    duplicate = {**NEW_USER, "email": "NOUVEAU@test.ci"}
    assert client.post("/api/users", json=duplicate).status_code == 409


def test_mot_de_passe_trop_court(client: TestClient, make_user) -> None:
    make_user(Role.admin)
    login(client, "admin@test.ci")
    response = client.post("/api/users", json={**NEW_USER, "password": "court"})
    assert response.status_code == 422
