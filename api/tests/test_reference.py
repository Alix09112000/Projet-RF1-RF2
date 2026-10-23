from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import City, Role, Segment
from tests.conftest import login


def test_reference_reservee_aux_connectes(client: TestClient) -> None:
    assert client.get("/api/reference").status_code == 401


def test_reference(client: TestClient, db: Session, make_user) -> None:
    db.add(City(code="ABJ", name="Abidjan", country="Côte d'Ivoire", currency="XOF"))
    db.add_all([Segment(code="B2C", name="Particuliers"), Segment(code="SME", name="Entreprises")])
    db.commit()
    make_user(Role.viewer)
    login(client, "viewer@test.ci")

    data = client.get("/api/reference").json()
    assert [c["code"] for c in data["cities"]] == ["ABJ"]
    assert [s["code"] for s in data["segments"]] == ["B2C", "SME"]
    assert data["versions"] == []
