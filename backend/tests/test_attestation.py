from app.attestation import artifact_digest, artifact_payload, build_artifact, canonical_json, evidence_hash, verify_artifact_signature
from app.key_registry import PublicKeyRecord, registry
from app.signing import sign_artifact
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.contracts import Evidence, EvidenceKind, SignalStatus, VerificationResponse, VerificationResult


def test_canonical_json_is_stable():
    assert canonical_json({"b": 2, "a": 1}) == canonical_json({"a": 1, "b": 2})


def test_evidence_hash_is_stable_and_order_sensitive():
    first = Evidence(signal="a", status=SignalStatus.AVAILABLE, kind=EvidenceKind.FACT, summary="a")
    second = Evidence(signal="b", status=SignalStatus.AVAILABLE, kind=EvidenceKind.FACT, summary="b")
    assert evidence_hash([first, second]) != evidence_hash([second, first])


def test_build_artifact_binds_media_and_evidence():
    evidence = [Evidence(signal="integrity", status=SignalStatus.AVAILABLE, summary="ok")]
    response = VerificationResponse(
        verification_id="v-1",
        sha256="a" * 64,
        result=VerificationResult.UNCERTAIN,
        confidence=0.0,
        signals=evidence,
        evidence=evidence,
    )
    artifact = build_artifact(response)
    assert artifact.media_sha256 == "a" * 64
    assert artifact.verification_id == "v-1"
    assert len(artifact.evidence_hash) == 64
    assert artifact.signature is None


def test_artifact_digest_ignores_signature_fields():
    evidence = [Evidence(signal="integrity", status=SignalStatus.AVAILABLE, summary="ok")]
    response = VerificationResponse(
        verification_id="v-2",
        sha256="b" * 64,
        result=VerificationResult.VERIFIED,
        confidence=0.9,
        signals=evidence,
        evidence=evidence,
    )
    artifact = build_artifact(response)
    signed_shape = artifact.model_copy(update={"signature": "signature", "signature_algorithm": "Ed25519:key-1"})
    assert artifact_payload(artifact) == artifact_payload(signed_shape)
    assert artifact_digest(artifact) == artifact_digest(signed_shape)


def test_artifact_digest_changes_when_bound_data_changes():
    evidence = [Evidence(signal="integrity", status=SignalStatus.AVAILABLE, summary="ok")]
    response = VerificationResponse(
        verification_id="v-3",
        sha256="c" * 64,
        result=VerificationResult.UNCERTAIN,
        confidence=0.1,
        signals=evidence,
        evidence=evidence,
    )
    artifact = build_artifact(response)
    changed = artifact.model_copy(update={"confidence": 0.2})
    assert artifact_digest(artifact) != artifact_digest(changed)


def test_signed_artifact_can_be_verified(monkeypatch):
    registry._keys.clear()
    private = Ed25519PrivateKey.generate()
    public_b64 = base64.b64encode(private.public_key().public_bytes_raw()).decode()
    monkeypatch.setenv("REALITYX_SIGNING_KEY_ID", "test-key")
    monkeypatch.setenv("REALITYX_SIGNING_PRIVATE_KEY_B64", base64.b64encode(private.private_bytes_raw()).decode())
    registry.register(PublicKeyRecord("test-key", "Ed25519", public_b64, "active", "now"))
    artifact = build_artifact(VerificationResponse(
        verification_id="v-verify",
        sha256="d" * 64,
        result=VerificationResult.VERIFIED,
        confidence=0.9,
        signals=[],
        evidence=[],
    ))
    signed = sign_artifact(artifact)
    assert verify_artifact_signature(signed) is True
    tampered = signed.model_copy(update={"confidence": 0.1})
    assert verify_artifact_signature(tampered) is False
