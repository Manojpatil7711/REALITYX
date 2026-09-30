import io
import uuid

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8)).save(buf, format="PNG")
    return buf.getvalue()


def test_idempotency_required():
    response = client.post("/v1/verify/image", files={"file": ("x.png", b"bad", "image/png")})
    assert response.status_code == 400


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_declared_mime_must_match_detected_format():
    response = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("x.png", _png(), "image/jpeg")},
    )
    assert response.status_code == 415


def test_valid_image_verification_returns_stable_contract():
    response = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("x.png", _png(), "image/png")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["protocol_version"] == "1.0"
    assert payload["result"] == "uncertain"
    assert payload["signals"]
    assert payload["sha256"]


def test_same_idempotency_key_returns_same_response_for_same_payload():
    key = str(uuid.uuid4())
    first = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": key},
        files={"file": ("x.png", _png(), "image/png")},
    )
    second = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": key},
        files={"file": ("x.png", _png(), "image/png")},
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json() == first.json()


def test_idempotency_key_cannot_be_reused_for_different_payload():
    key = str(uuid.uuid4())
    first = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": key},
        files={"file": ("x.png", _png(), "image/png")},
    )
    different = io.BytesIO()
    Image.new("RGB", (9, 9)).save(different, format="PNG")
    second = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": key},
        files={"file": ("x.png", different.getvalue(), "image/png")},
    )
    assert first.status_code == 200
    assert second.status_code == 409


def test_empty_upload_is_rejected():
    response = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert response.status_code == 400


def test_rate_limit_returns_retry_after(monkeypatch):
    from app import routes

    class Blocked:
        allowed = False
        retry_after_seconds = 17

    monkeypatch.setattr(routes.image_verify_limiter, "check", lambda identity: Blocked())
    response = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("x.png", _png(), "image/png")},
    )
    assert response.status_code == 429
    assert response.headers["retry-after"] == "17"
