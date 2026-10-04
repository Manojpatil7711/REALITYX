from app.attestation import artifact_digest, artifact_payload, build_artifact, canonical_json, evidence_hash
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
