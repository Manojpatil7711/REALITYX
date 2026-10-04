from app.contracts import Evidence, EvidenceKind, ProfessionalEvidenceStatus, SignalStatus, SignalVerdict, VerificationResponse, VerificationResult
from app.professional_evidence import enrich_professional_evidence_item


def test_cctv_evidence_gets_frame_location_and_identity_boundary():
    item = Evidence(
        evidence_id="cctv-1",
        source_group="cctv",
        signal="cctv.face_visibility",
        status=SignalStatus.AVAILABLE,
        kind=EvidenceKind.FACT,
        summary="face visibility",
        details={
            "frame_index": 42,
            "timestamp_ms": 1400,
            "limitations": ["Face visibility does not establish identity."],
        },
    )
    response = VerificationResponse(
        verification_id="12345678-1234-1234-1234-123456789012",
        sha256="a" * 64,
        result=VerificationResult.UNCERTAIN,
        confidence=0.0,
        signals=[item],
        evidence=[item],
    )

    result = enrich_professional_evidence_item(
        item,
        response=response,
        status=ProfessionalEvidenceStatus.WEAK,
    )

    assert result.location == "frame=42;timestamp_ms=1400"
    assert "identity remains unverified" in result.summary.lower()


def test_non_cctv_evidence_keeps_original_summary():
    item = Evidence(
        evidence_id="e1",
        source_group="engine",
        signal="image_forensics",
        status=SignalStatus.AVAILABLE,
        kind=EvidenceKind.FACT,
        summary="ordinary evidence",
    )
    response = VerificationResponse(
        verification_id="12345678-1234-1234-1234-123456789012",
        sha256="a" * 64,
        result=VerificationResult.UNCERTAIN,
        confidence=0.0,
        signals=[item],
        evidence=[item],
    )

    result = enrich_professional_evidence_item(
        item,
        response=response,
        status=ProfessionalEvidenceStatus.WEAK,
    )

    assert result.summary == "ordinary evidence"
    assert result.location is None
