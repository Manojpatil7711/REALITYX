import base64
import io
import uuid

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from PIL import Image

from app.key_registry import PublicKeyRecord, registry
from app.main import app
from app.receipt_store import store

client = TestClient(app)


def _png() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (16, 10)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_receipt_is_published_after_verification(monkeypatch):
    private = Ed25519PrivateKey.generate()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "test-key")
    public_b64 = base64.b64encode(private.public_key().public_bytes_raw()).decode()
    monkeypatch.setenv(
        "REALITYX_SIGNING_PRIVATE_KEY_B64",
        base64.b64encode(private.private_bytes_raw()).decode(),
    )
    registry.register(PublicKeyRecord("test-key", "Ed25519", public_b64, "active", "test"))

    verification_id = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("test.png", _png(), "image/png")},
    ).json()["verification_id"]

    response = client.get(f"/v1/receipts/{verification_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["receipt"]["verification_id"] == verification_id
    assert body["receipt"]["signature_algorithm"] == "Ed25519:test-key"
    assert body["receipt"]["signature"]
    assert body["attested"] is True
    assert len(body["receipt_digest"]) == 64


def test_receipt_not_found():
    response = client.get(f"/v1/receipts/{uuid.uuid4()}")
    assert response.status_code == 404


def test_receipt_signature_verifies_independently(monkeypatch):
    private = Ed25519PrivateKey.generate()
    public_b64 = base64.b64encode(private.public_key().public_bytes_raw()).decode()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "verify-key")
    monkeypatch.setenv(
        "REALITYX_SIGNING_PRIVATE_KEY_B64",
        base64.b64encode(private.private_bytes_raw()).decode(),
    )
    registry.register(PublicKeyRecord("verify-key", "Ed25519", public_b64, "active", "test"))

    verification_id = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("test.png", _png(), "image/png")},
    ).json()["verification_id"]

    response = client.get(f"/v1/receipts/{verification_id}/verify")

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["algorithm"] == "Ed25519"
    assert body["key_id"] == "verify-key"


def test_receipt_signature_rejects_tampering(monkeypatch):
    private = Ed25519PrivateKey.generate()
    public_b64 = base64.b64encode(private.public_key().public_bytes_raw()).decode()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "tamper-key")
    monkeypatch.setenv(
        "REALITYX_SIGNING_PRIVATE_KEY_B64",
        base64.b64encode(private.private_bytes_raw()).decode(),
    )
    registry.register(PublicKeyRecord("tamper-key", "Ed25519", public_b64, "active", "test"))

    verification_id = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("test.png", _png(), "image/png")},
    ).json()["verification_id"]

    artifact = store.get(verification_id)
    assert artifact is not None
    store.put(artifact.model_copy(update={"result": "INAUTHENTIC"}))

    response = client.get(f"/v1/receipts/{verification_id}/verify")

    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert response.json()["reason"] == "Signature verification failed"


def test_receipt_signature_rejects_unknown_key(monkeypatch):
    private = Ed25519PrivateKey.generate()
    public_b64 = base64.b64encode(private.public_key().public_bytes_raw()).decode()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "known-key")
    monkeypatch.setenv(
        "REALITYX_SIGNING_PRIVATE_KEY_B64",
        base64.b64encode(private.private_bytes_raw()).decode(),
    )
    registry.register(PublicKeyRecord("known-key", "Ed25519", public_b64, "active", "test"))

    verification_id = client.post(
        "/v1/verify/image",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        files={"file": ("test.png", _png(), "image/png")},
    ).json()["verification_id"]

    artifact = store.get(verification_id)
    assert artifact is not None
    store.put(artifact.model_copy(update={"signature_algorithm": "Ed25519:missing-key"}))

    response = client.get(f"/v1/receipts/{verification_id}/verify")

    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert response.json()["reason"] == "Signing key is unavailable"
