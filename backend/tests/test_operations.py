from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_workflow_profiles_are_clear_and_non_empty():
    response = client.get("/v1/operations/profiles")
    assert response.status_code == 200
    profiles = response.json()["profiles"]
    assert len(profiles) >= 5
    assert {item["id"] for item in profiles} >= {"government", "legal", "media", "business", "public"}
    assert all(item["purpose"] and item["flow"] for item in profiles)


def test_capability_watch_exposes_only_safe_aggregate_state():
    response = client.get("/v1/operations/capability-watch")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["engine_count"] >= 1
    assert len(payload["capability_fingerprint"]) == 64
    assert "private_engine" not in payload["capability_fingerprint"]
