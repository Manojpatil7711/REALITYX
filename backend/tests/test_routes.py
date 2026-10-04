import io
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _png() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (16, 10)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_verify_image_requires_idempotency_key():
    response = client.post(
        "/v1/verify/image",
        files={"file": ("test.png", _png(), "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Idempotency-Key is required"


def test_verify_image_rejects_invalid_idempotency_key():
    response = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": "not-a-uuid"},
        files={"file": ("test.png", _png(), "image/png")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Idempotency-Key must be a UUID"


def test_verify_image_returns_conservative_uncertain_without_verdict_engine():
    response = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("test.png", _png(), "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["result"] == "uncertain"
    assert body["confidence"] == 0.0
    assert all(signal["verdict"] is None for signal in body["signals"])


def test_verify_image_rejects_mismatched_content_type():
    response = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("test.png", _png(), "image/jpeg")},
    )
    assert response.status_code == 415


def test_verify_image_idempotency_replays_same_response():
    key = str(uuid.uuid4())
    payload = {"file": ("test.png", _png(), "image/png")}

    first = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": key},
        files=payload,
    )
    second = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": key},
        files={"file": ("test.png", _png(), "image/png")},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json() == first.json()


def test_verify_image_rejects_concurrent_duplicate_request(monkeypatch):
    started = Event()
    release = Event()

    def blocked_pipeline(data: bytes, verification_id: str, fingerprint: str):
        started.set()
        assert release.wait(timeout=5)
        return []

    monkeypatch.setattr("app.routes.run_signal_pipeline", blocked_pipeline)

    key = str(uuid.uuid4())
    payload = {"file": ("test.png", _png(), "image/png")}

    with ThreadPoolExecutor(max_workers=2) as executor:
        first_future = executor.submit(
            client.post,
            "/v1/verify/image",
            headers={"Idempotency-Key": key},
            files=payload,
        )
        assert started.wait(timeout=5)

        second = client.post(
            "/v1/verify/image",
            headers={"Idempotency-Key": key},
            files={"file": ("test.png", _png(), "image/png")},
        )

        release.set()
        first = first_future.result(timeout=5)

    assert second.status_code == 409
    assert second.headers["Retry-After"] == "2"
    assert first.status_code == 200
