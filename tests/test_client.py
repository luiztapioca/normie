from fastapi.testclient import TestClient
from ..run import app

client = TestClient(app)


def test_normalise_basic():
    response = client.post("/api/normalise", params={"msg": "pq vc n vem"})
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert isinstance(data["result"], str)
