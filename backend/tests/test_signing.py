import base64

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.attestation import artifact_digest
from app.contracts import VerificationArtifact, VerificationResult
from app.key_registry import PublicKeyRecord, registry
from app.signing import sign_artifact


def artifact():
    return VerificationArtifact(
        verification_id="v-1",
        media_sha256="a" * 64,
        result=VerificationResult.UNCERTAIN,
        confidence=0.0,
        evidence_hash="b" * 64,
        evidence_graph_digest="d" * 64,
    )


def reset_registry():
    registry._keys.clear()


def test_digest_binds_signature_key_identity_but_excludes_signature_bytes():
    original = artifact()
    signed = original.model_copy(update={"signature_algorithm": "Ed25519:k1", "signature": "abc"})
    assert artifact_digest(original) != artifact_digest(signed)
    signed_again = signed.model_copy(update={"signature": "different"})
    assert artifact_digest(signed) == artifact_digest(signed_again)


def test_sign_artifact_with_env_key(monkeypatch):
    reset_registry()
    private = Ed25519PrivateKey.generate()
    raw = private.private_bytes_raw()
    public_raw = private.public_key().public_bytes_raw()
    public_b64 = base64.b64encode(public_raw).decode()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "k1")
    monkeypatch.setenv("REALITYX_SIGNING_PRIVATE_KEY_B64", base64.b64encode(raw).decode())
    registry.register(PublicKeyRecord("k1", "Ed25519", public_b64, "active", "now"))

    signed = sign_artifact(artifact())
    assert signed.signature_algorithm == "Ed25519:k1"
    assert signed.signature is not None
    from app.attestation import artifact_payload
    private.public_key().verify(base64.b64decode(signed.signature), artifact_payload(signed))


def test_sign_artifact_rejects_unregistered_key(monkeypatch):
    reset_registry()
    private = Ed25519PrivateKey.generate()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "missing")
    monkeypatch.setenv("REALITYX_SIGNING_PRIVATE_KEY_B64", base64.b64encode(private.private_bytes_raw()).decode())
    with pytest.raises(RuntimeError, match="not registered"):
        sign_artifact(artifact())


def test_sign_artifact_rejects_mismatched_public_key(monkeypatch):
    reset_registry()
    private = Ed25519PrivateKey.generate()
    other = Ed25519PrivateKey.generate()
    registry.register(PublicKeyRecord(
        "k1", "Ed25519", base64.b64encode(other.public_key().public_bytes_raw()).decode(), "active", "now"
    ))
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "k1")
    monkeypatch.setenv("REALITYX_SIGNING_PRIVATE_KEY_B64", base64.b64encode(private.private_bytes_raw()).decode())
    with pytest.raises(RuntimeError, match="does not match"):
        sign_artifact(artifact())


def test_required_signing_fails_closed_without_credentials(monkeypatch):
    reset_registry()
    monkeypatch.delenv("REALITYX_SIGNING_KEY_ID", raising=False)
    monkeypatch.delenv("REALITYX_SIGNING_PRIVATE_KEY_B64", raising=False)
    monkeypatch.setenv("REALITYX_REQUIRE_SIGNING", "true")

    with pytest.raises(RuntimeError, match="signing is required"):
        sign_artifact(artifact())


def test_signing_remains_optional_for_development(monkeypatch):
    reset_registry()
    monkeypatch.delenv("REALITYX_SIGNING_KEY_ID", raising=False)
    monkeypatch.delenv("REALITYX_SIGNING_PRIVATE_KEY_B64", raising=False)
    monkeypatch.delenv("REALITYX_REQUIRE_SIGNING", raising=False)

    unsigned = sign_artifact(artifact())
    assert unsigned.signature is None
    assert unsigned.signature_algorithm is None
