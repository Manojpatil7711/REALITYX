import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.premium.owner_access import require_owner

client = TestClient(app)


def test_owner_control_plane_requires_configuration(monkeypatch):
    monkeypatch.delenv("REALITYX_OWNER_MASTER_KEY", raising=False)
    response = client.get("/v1/owner/status")
    assert response.status_code == 503


def test_owner_control_plane_rejects_invalid_key(monkeypatch):
    monkeypatch.setenv("REALITYX_OWNER_MASTER_KEY", "test-owner-secret")
    response = client.get(
        "/v1/owner/status",
        headers={"x-realityx-master-key": "wrong-secret"},
    )
    assert response.status_code == 403


def test_owner_control_plane_accepts_correct_key(monkeypatch):
    monkeypatch.setenv("REALITYX_OWNER_MASTER_KEY", "test-owner-secret")
    response = client.get(
        "/v1/owner/status",
        headers={"x-realityx-master-key": "test-owner-secret"},
    )
    assert response.status_code == 200
    assert response.json() == {"access": "owner", "control_plane": "private"}


def test_owner_control_plane_does_not_expose_secret(monkeypatch):
    monkeypatch.setenv("REALITYX_OWNER_MASTER_KEY", "super-secret-value")
    response = client.get(
        "/v1/owner/status",
        headers={"x-realityx-master-key": "super-secret-value"},
    )
    assert "super-secret-value" not in response.text
