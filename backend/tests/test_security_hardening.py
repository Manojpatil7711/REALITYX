import os

from fastapi.testclient import TestClient

from app.main import app
from app.premium.owner_access import require_owner


def test_security_headers_are_present():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"].startswith("camera=()")
    assert "default-src 'none'" in response.headers["Content-Security-Policy"]


def test_owner_auth_requires_secret(monkeypatch):
    monkeypatch.delenv("REALITYX_OWNER_MASTER_KEY", raising=False)
    client = TestClient(app)
    response = client.get("/v1/owner/status")
    assert response.status_code == 503


def test_owner_auth_rejects_invalid_secret(monkeypatch):
    monkeypatch.setenv("REALITYX_OWNER_MASTER_KEY", "test-owner-secret")
    client = TestClient(app)
    response = client.get(
        "/v1/owner/status",
        headers={"X-REALITYX-Master-Key": "wrong-secret"},
    )
    assert response.status_code == 403
