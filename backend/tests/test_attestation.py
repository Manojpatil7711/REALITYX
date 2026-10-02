from app.attestation import build_artifact, canonical_json, evidence_hash
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
