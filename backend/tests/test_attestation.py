from app.attestation import artifact_digest, artifact_payload, build_artifact, canonical_json, evidence_hash, verify_artifact_signature
from app.key_registry import PublicKeyRecord, registry
from app.signing import sign_artifact
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from app.contracts import Evidence, EvidenceKind, SignalStatus, VerificationResponse, VerificationResult


def _response(verification_id="v-1", sha="a" * 64):
    evidence = [Evidence(signal="integrity", status=SignalStatus.AVAILABLE, summary="ok")]
    return VerificationResponse(verification_id=verification_id, sha256=sha, result=VerificationResult.UNCERTAIN, confidence=0.0, signals=evidence, evidence=evidence, evidence_graph_digest="d" * 64)


def test_canonical_json_is_stable():
    assert canonical_json({"b": 2, "a": 1}) == canonical_json({"a": 1, "b": 2})


def test_evidence_hash_is_stable_and_order_sensitive():
    first = Evidence(signal="a", status=SignalStatus.AVAILABLE, kind=EvidenceKind.FACT, summary="a")
    second = Evidence(signal="b", status=SignalStatus.AVAILABLE, kind=EvidenceKind.FACT, summary="b")
    assert evidence_hash([first, second]) != evidence_hash([second, first])


def test_build_artifact_binds_media_evidence_and_policy():
    artifact = build_artifact(_response())
    assert artifact.media_sha256 == "a" * 64
    assert artifact.verification_id == "v-1"
    assert len(artifact.evidence_hash) == 64
    assert artifact.evidence_graph_digest == "d" * 64
    assert artifact.policy_version == "2050.1"
    assert artifact.signature is None


def test_build_artifact_requires_provenance_digest():
    response = _response()
    response.evidence_graph_digest = ""
    try:
        build_artifact(response)
    except ValueError as exc:
        assert "evidence graph digest" in str(exc)
    else:
        raise AssertionError("missing provenance digest must fail closed")


def test_artifact_digest_ignores_signature_fields():
    artifact = build_artifact(_response("v-2", "b" * 64))
    signed_shape = artifact.model_copy(update={"signature": "signature", "signature_algorithm": "Ed25519:key-1"})
    assert artifact_payload(artifact) != artifact_payload(signed_shape)
    assert artifact_digest(artifact) != artifact_digest(signed_shape)


def test_artifact_digest_changes_when_bound_data_changes():
    artifact = build_artifact(_response("v-3", "c" * 64))
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
        evidence_graph_digest="d" * 64,
    ))
    signed = sign_artifact(artifact)
    assert verify_artifact_signature(signed) is True
    tampered = signed.model_copy(update={"confidence": 0.1})
    assert verify_artifact_signature(tampered) is False
