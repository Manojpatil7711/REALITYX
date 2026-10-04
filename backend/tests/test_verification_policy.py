from app.contracts import Evidence, EvidenceKind, SignalStatus, SignalVerdict, VerificationResult
from app.risk_assessment import RiskDomain, RiskLevel, RecommendedAction
from app.verification_policy import (
    AuthorityStatus, OriginalityResult, determine_originality, evaluate_verification,
)

def ev(i, group, signal, *, parents=None, risk_class=None, verdict=None, confidence=0.9):
    details = {"risk_class": risk_class} if risk_class else {}
    return Evidence(evidence_id=i, source_group=group, signal=signal,
                    status=SignalStatus.AVAILABLE, kind=EvidenceKind.VERDICT,
                    summary=signal, details=details, parent_evidence_ids=parents or [],
                    verdict=verdict, confidence=confidence)

def test_same_root_cannot_create_two_independent_sources():
    evidence = [
        ev("root", "camera-a", "tamper", verdict=SignalVerdict.MANIPULATED),
        ev("derived-1", "engine-b", "document_tamper", parents=["root"],
           risk_class="document_tamper", verdict=SignalVerdict.MANIPULATED),
        ev("derived-2", "engine-c", "provenance_invalid", parents=["derived-1"],
           risk_class="provenance_invalid", verdict=SignalVerdict.MANIPULATED),
    ]
    result = evaluate_verification(evidence, domain=RiskDomain.DOCUMENT,
                                    fusion_result=VerificationResult.INAUTHENTIC,
                                    fusion_confidence=0.95)
    assert result.independent_source_count == 1
    assert result.result is VerificationResult.UNCERTAIN
    assert result.risk.action is RecommendedAction.REVERIFY

def test_two_independent_roots_can_support_high_risk():
    evidence = [
        ev("a", "source-a", "document_tamper", risk_class="document_tamper"),
        ev("b", "source-b", "provenance_invalid", risk_class="provenance_invalid"),
    ]
    result = evaluate_verification(evidence, domain=RiskDomain.MEDIA,
                                    fusion_result=VerificationResult.INAUTHENTIC,
                                    fusion_confidence=0.94)
    assert result.independent_source_count == 2
    assert result.risk.level is RiskLevel.HIGH
    assert result.risk.action is RecommendedAction.BLOCK_PENDING_REVIEW

def test_failed_evidence_is_not_a_negative_signal():
    failed = Evidence(evidence_id="failed", source_group="x", signal="tamper",
                      status=SignalStatus.FAILED, kind=EvidenceKind.VERDICT,
                      summary="failed", verdict=SignalVerdict.MANIPULATED, confidence=0.99)
    result = evaluate_verification([failed], domain=RiskDomain.MEDIA)
    assert result.independent_source_count == 0
    assert result.result is VerificationResult.UNCERTAIN

def test_conflict_forces_uncertain():
    evidence = [
        ev("a", "source-a", "authenticity", verdict=SignalVerdict.AUTHENTIC),
        ev("b", "source-b", "authenticity", verdict=SignalVerdict.MANIPULATED),
    ]
    result = evaluate_verification(evidence, domain=RiskDomain.MEDIA,
                                    fusion_result=VerificationResult.UNCERTAIN,
                                    fusion_confidence=0.8, fusion_conflict=True)
    assert result.result is VerificationResult.UNCERTAIN
    assert result.confidence <= 0.49

def test_government_verdict_without_authority_cannot_be_verified_original():
    evidence = [ev("a", "source-a", "integrity_ok", verdict=SignalVerdict.VERIFIED)]
    result = evaluate_verification(evidence, domain=RiskDomain.GOVERNMENT,
                                    fusion_result=VerificationResult.VERIFIED,
                                    fusion_confidence=0.98)
    assert result.result is VerificationResult.UNCERTAIN
    assert result.risk.level is RiskLevel.UNCERTAIN

def test_authority_can_unlock_government_verification():
    evidence = [ev("a", "source-a", "integrity_ok", verdict=SignalVerdict.VERIFIED)]
    result = evaluate_verification(evidence, domain=RiskDomain.GOVERNMENT,
                                    fusion_result=VerificationResult.VERIFIED,
                                    fusion_confidence=0.98,
                                    authority_status=AuthorityStatus.VERIFIED)
    assert result.result is VerificationResult.VERIFIED

def test_identical_documents_without_authority_are_undetermined():
    assert determine_originality(
        authoritative_status=AuthorityStatus.UNAVAILABLE
    ) is OriginalityResult.UNABLE_TO_DETERMINE

def test_originality_states_never_depend_on_similarity():
    assert determine_originality(
        authoritative_status=AuthorityStatus.VERIFIED, duplicate=True
    ) is OriginalityResult.DUPLICATE


def test_malformed_provenance_fails_closed():
    evidence = [
        ev("a", "source-a", "authenticity", parents=["missing-parent"],
           verdict=SignalVerdict.AUTHENTIC, confidence=0.99),
    ]
    result = evaluate_verification(
        evidence,
        domain=RiskDomain.MEDIA,
        fusion_result=VerificationResult.VERIFIED,
        fusion_confidence=0.99,
    )
    assert result.result is VerificationResult.UNCERTAIN
    assert result.confidence == 0.0
    assert result.independent_source_count == 0
    assert result.evidence_graph_digest == ""
    assert result.risk.action is RecommendedAction.REVERIFY
