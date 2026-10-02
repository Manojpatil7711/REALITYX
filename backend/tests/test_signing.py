import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.contracts import VerificationArtifact, VerificationResult
from app.signing import artifact_digest, sign_artifact


def artifact():
    return VerificationArtifact(
        verification_id="v-1",
        media_sha256="a" * 64,
        result=VerificationResult.UNCERTAIN,
        confidence=0.0,
        evidence_hash="b" * 64,
    )


def test_digest_excludes_signature_fields():
    original = artifact()
    signed = original.model_copy(update={"signature_algorithm": "Ed25519:k1", "signature": "abc"})
    assert artifact_digest(original) == artifact_digest(signed)


def test_sign_artifact_with_env_key(monkeypatch):
    private = Ed25519PrivateKey.generate()
    raw = private.private_bytes_raw()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "k1")
    monkeypatch.setenv("REALITYX_SIGNING_PRIVATE_KEY_B64", base64.b64encode(raw).decode())

    signed = sign_artifact(artifact())
    assert signed.signature_algorithm == "Ed25519:k1"
    assert signed.signature is not None
    public = private.public_key()
    payload_artifact = signed.model_copy(update={"signature": None, "signature_algorithm": None})
    from app.attestation import canonical_json
    payload = canonical_json(payload_artifact.model_dump(mode="json", exclude={"signature", "signature_algorithm"}))
    public.verify(base64.b64decode(signed.signature), payload)
