from app.contracts import Evidence, EvidenceKind, SignalStatus
from app.risk_assessment import RiskDomain, RiskLevel, RecommendedAction, assess_risk


def ev(signal, group, *, risk_class=None, confidence=0.9):
    details = {"risk_class": risk_class} if risk_class else {}
    return Evidence(
        signal=signal, source_group=group, status=SignalStatus.AVAILABLE,
        kind=EvidenceKind.FACT, summary=signal, details=details,
        confidence=confidence,
    )


def test_no_evidence_requires_reverification():
    result = assess_risk([], domain=RiskDomain.GOVERNMENT)
    assert result.level is RiskLevel.UNCERTAIN
    assert result.action is RecommendedAction.REVERIFY


def test_single_high_risk_signal_abstains():
    result = assess_risk([
        ev("identity_tamper", "engine-a", risk_class="identity_tamper"),
    ], domain=RiskDomain.IDENTITY)
    assert result.level is RiskLevel.UNCERTAIN
    assert result.action is RecommendedAction.REVERIFY
    assert result.confidence <= 0.49


def test_independent_high_risk_sources_require_review():
    result = assess_risk([
        ev("identity_tamper", "engine-a", risk_class="identity_tamper"),
        ev("provenance_invalid", "provenance-b", risk_class="provenance_invalid"),
    ], domain=RiskDomain.IDENTITY)
    assert result.level is RiskLevel.HIGH
    assert result.action is RecommendedAction.BLOCK_PENDING_REVIEW
    assert result.independent_sources == 2


def test_critical_signal_is_not_sufficient_without_independence():
    result = assess_risk([
        ev("government_document_tamper", "engine-a",
           risk_class="government_document_tamper"),
    ], domain=RiskDomain.GOVERNMENT)
    assert result.level is RiskLevel.UNCERTAIN


def test_normal_evidence_does_not_create_risk():
    result = assess_risk([ev("integrity_ok", "engine-a")], domain=RiskDomain.MEDIA)
    assert result.level is RiskLevel.NONE
    assert result.action is RecommendedAction.ALLOW
