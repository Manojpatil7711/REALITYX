from app.contracts import Evidence, EvidenceKind, SignalStatus, SignalVerdict, VerificationResult
from app.evidence_fusion import fuse_evidence


def signal(verdict=None, confidence=0.9, status=SignalStatus.AVAILABLE, name="test"):
    return Evidence(
        signal=name,
        status=status,
        summary="test",
        kind=EvidenceKind.VERDICT if verdict is not None else EvidenceKind.FACT,
        verdict=SignalVerdict(verdict) if verdict is not None else None,
        confidence=confidence,
    )


def test_empty_evidence_abstains():
    decision = fuse_evidence([])
    assert decision.result is VerificationResult.UNCERTAIN
    assert decision.confidence == 0.0


def test_failed_signal_is_not_negative_evidence():
    decision = fuse_evidence([signal("authentic", 0.9), signal(status=SignalStatus.FAILED)])
    assert decision.result is VerificationResult.UNCERTAIN
    assert decision.confidence < 0.70


def test_weak_evidence_abstains():
    decision = fuse_evidence([signal("authentic", 0.69)])
    assert decision.result is VerificationResult.UNCERTAIN


def test_conflicting_evidence_abstains():
    decision = fuse_evidence([signal("authentic", 0.95), signal("manipulated", 0.94)])
    assert decision.result is VerificationResult.UNCERTAIN


def test_consistent_negative_evidence_can_be_inauthentic():
    decision = fuse_evidence([
        signal("manipulated", 0.95),
        signal("ai_generated", 0.92),
        signal("inauthentic", 0.90),
    ])
    assert decision.result is VerificationResult.INAUTHENTIC
    assert decision.confidence >= 0.70


def test_missing_verdict_does_not_create_a_public_verdict():
    decision = fuse_evidence([signal(None, 0.99)])
    assert decision.result is VerificationResult.UNCERTAIN
    assert decision.confidence == 0.0


def test_factual_signals_do_not_inflate_verdict_coverage():
    verdict_only = fuse_evidence([signal("authentic", 0.9, name="model")])

    with_facts = fuse_evidence([
        signal("authentic", 0.9, name="model"),
        signal(None, 1.0, name="integrity"),
        signal(None, 1.0, name="image_structure"),
        signal(None, 1.0, name="metadata"),
    ])

    assert with_facts.result is verdict_only.result
    assert with_facts.confidence == verdict_only.confidence
