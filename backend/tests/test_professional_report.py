from app.contracts import Evidence, EvidenceKind, ProfessionalEvidenceStatus, SignalStatus, SignalVerdict, VerificationResponse, VerificationResult
from app.professional_report import build_professional_report


def _response(result=VerificationResult.UNCERTAIN, confidence=0.0, sources=0, conflict=False, verdict=None, status=SignalStatus.AVAILABLE):
    evidence = [
        Evidence(
            evidence_id="e1",
            source_group="engine-a",
            signal="image_forensics",
            status=status,
            kind=EvidenceKind.VERDICT,
            summary="test evidence",
            verdict=verdict if verdict is not None else (SignalVerdict.INAUTHENTIC if result is VerificationResult.INAUTHENTIC else None),
            confidence=confidence if confidence else None,
        )
    ]
    return VerificationResponse(
        verification_id="12345678-1234-1234-1234-123456789012",
        sha256="a" * 64,
        result=result,
        confidence=confidence,
        signals=evidence,
        evidence=evidence,
        independent_source_count=sources,
        conflict=conflict,
        evidence_graph_digest="b" * 64,
    )


def test_professional_report_has_plain_language_conclusion():
    report = build_professional_report(_response(VerificationResult.INAUTHENTIC, 0.91, 3))
    assert report.verdict is VerificationResult.INAUTHENTIC
    assert report.evidence_strength.value == "strong"
    assert "manipulation" in report.conclusion.lower()
    assert report.artifact_sha256 == "a" * 64


def test_professional_report_marks_conflict():
    report = build_professional_report(_response(confidence=0.4, sources=2, conflict=True))
    assert report.evidence_strength.value == "conflicting"
    assert report.conflict is True
    assert report.evidence[0].status is ProfessionalEvidenceStatus.CONFLICTING


def test_uncertain_report_explains_limitations():
    report = build_professional_report(_response())
    assert report.evidence_strength.value == "insufficient"
    assert any("insufficient" in item.lower() for item in report.limitations)


def test_negative_forensic_verdict_maps_to_negative_status():
    report = build_professional_report(_response(
        VerificationResult.INAUTHENTIC, 0.91, 2, verdict=SignalVerdict.AI_GENERATED
    ))
    assert report.evidence[0].status is ProfessionalEvidenceStatus.NEGATIVE


def test_failed_evidence_maps_to_not_available():
    report = build_professional_report(_response(
        status=SignalStatus.FAILED, verdict=SignalVerdict.MANIPULATED
    ))
    assert report.evidence[0].status is ProfessionalEvidenceStatus.NOT_AVAILABLE


def test_high_confidence_authentic_evidence_maps_to_strong():
    report = build_professional_report(_response(
        VerificationResult.VERIFIED, 0.9, 2, verdict=SignalVerdict.AUTHENTIC
    ))
    assert report.evidence[0].status is ProfessionalEvidenceStatus.STRONG
