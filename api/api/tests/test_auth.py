from fastapi.testclient import TestClient

from app.models import Role
from tests.conftest import PASSWORD, login


def test_login_puis_me(client: TestClient, make_user) -> None:
    make_user(Role.contributor, email="m.amou@test.ci")
    login(client, "M.Amou@test.ci ")  # casse et espaces ignorés
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "m.amou@test.ci"
    assert response.json()["role"] == "contributor"


def test_mauvais_mot_de_passe(client: TestClient, make_user) -> None:
    make_user(Role.contributor)
    response = client.post(
        "/api/auth/login", json={"email": "contributor@test.ci", "password": "faux"}
    )
    assert response.status_code == 401
    assert "rf_session" not in response.cookies


def test_compte_inactif_refuse(client: TestClient, make_user) -> None:
    make_user(Role.contributor, active=False)
    response = client.post(
        "/api/auth/login", json={"email": "contributor@test.ci", "password": PASSWORD}
    )
    assert response.status_code == 401


def test_me_sans_session(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401


def test_jeton_falsifie(client: TestClient) -> None:
    client.cookies.set("rf_session", "pas-un-jeton")
    assert client.get("/api/auth/me").status_code == 401


def test_deconnexion(client: TestClient, make_user) -> None:
    make_user(Role.viewer)
    login(client, "viewer@test.ci")
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401
