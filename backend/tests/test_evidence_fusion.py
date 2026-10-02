from app.contracts import Evidence, SignalStatus
from app.evidence_fusion import fuse_evidence


def signal(verdict=None, confidence=0.9, status=SignalStatus.AVAILABLE):
    details = {} if verdict is None else {"verdict": verdict}
    return Evidence(
        signal="test",
        status=status,
        summary="test",
        details=details,
        confidence=confidence,
    )


def test_empty_evidence_abstains():
    decision = fuse_evidence([])
    assert decision.result == "uncertain"
    assert decision.confidence == 0.0


def test_failed_signal_is_not_negative_evidence():
    decision = fuse_evidence([signal("authentic", 0.9), signal(status=SignalStatus.FAILED)])
    assert decision.result == "uncertain"
    assert decision.confidence < 0.70


def test_weak_evidence_abstains():
    decision = fuse_evidence([signal("authentic", 0.69)])
    assert decision.result == "uncertain"


def test_conflicting_evidence_abstains():
    decision = fuse_evidence([signal("authentic", 0.95), signal("manipulated", 0.94)])
    assert decision.result == "uncertain"


def test_consistent_negative_evidence_can_be_inauthentic():
    decision = fuse_evidence([
        signal("manipulated", 0.95),
        signal("ai_generated", 0.92),
        signal("inauthentic", 0.90),
    ])
    assert decision.result == "inauthentic"
    assert decision.confidence >= 0.70


def test_missing_verdict_does_not_create_a_public_verdict():
    decision = fuse_evidence([signal(None, 0.99)])
    assert decision.result == "uncertain"
