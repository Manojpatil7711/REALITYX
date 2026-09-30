import uuid
from fastapi.testclient import TestClient
from app.main import app

def test_idempotency_required():
    client = TestClient(app)
    response = client.post("/v1/verify/image", files={"file": ("x.png", b"bad", "image/png")})
    assert response.status_code == 400

def test_health():
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"
