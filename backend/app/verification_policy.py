"""Unified 2050 verification policy."""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from .contracts import Evidence, VerificationResult
from .evidence_graph import EvidenceGraph
from .risk_assessment import RecommendedAction, RiskAssessment, RiskDomain, RiskLevel, assess_risk

POLICY_VERSION = "2050.1"

class AuthorityStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    VERIFIED = "verified"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"

class OriginalityResult(StrEnum):
    VERIFIED_ORIGINAL = "verified_original"
    VERIFIED_COPY = "verified_copy"
    MANIPULATED = "manipulated"
    DUPLICATE = "duplicate"
    UNABLE_TO_DETERMINE = "unable_to_determine"

@dataclass(frozen=True)
class UnifiedVerificationDecision:
    result: VerificationResult
    confidence: float
    risk: RiskAssessment
    evidence_graph_digest: str
    independent_source_count: int
    conflict: bool
    policy_version: str
    authority_status: AuthorityStatus

def evaluate_verification(evidence: list[Evidence], *, domain: RiskDomain = RiskDomain.UNKNOWN,
                          fusion_result: VerificationResult = VerificationResult.UNCERTAIN,
                          fusion_confidence: float = 0.0, fusion_conflict: bool = False,
                          authority_status: AuthorityStatus = AuthorityStatus.NOT_REQUIRED) -> UnifiedVerificationDecision:
    usable = [e for e in evidence if e.status.value == "available" and e.kind.value in {"fact", "verdict"}]
    graph = EvidenceGraph.from_evidence(usable)
    independent = len(graph.independent_source_groups(usable))
    risk = assess_risk(usable, domain=domain)
    result, confidence = fusion_result, fusion_confidence
    if risk.level in {RiskLevel.HIGH, RiskLevel.CRITICAL} and independent < 2:
        result, confidence = VerificationResult.UNCERTAIN, min(confidence, 0.49)
        risk = RiskAssessment(domain, RiskLevel.UNCERTAIN, min(risk.confidence, 0.49),
                              RecommendedAction.REVERIFY, risk.reasons, independent)
    authority_required = domain in {RiskDomain.IDENTITY, RiskDomain.DOCUMENT, RiskDomain.GOVERNMENT}
    if authority_required and authority_status is not AuthorityStatus.VERIFIED:
        if result is VerificationResult.VERIFIED:
            result = VerificationResult.UNCERTAIN
        confidence = min(confidence, 0.49)
        if risk.level is RiskLevel.NONE:
            risk = RiskAssessment(domain, RiskLevel.UNCERTAIN, min(risk.confidence, 0.49),
                                  RecommendedAction.REVERIFY,
                                  ("Authoritative verification is unavailable; originality cannot be established.",),
                                  independent)
    if fusion_conflict:
        result, confidence = VerificationResult.UNCERTAIN, min(confidence, 0.49)
    return UnifiedVerificationDecision(result, round(max(0.0, min(1.0, confidence)), 4),
                                       risk, graph.digest(), independent, fusion_conflict,
                                       POLICY_VERSION, authority_status)

def determine_originality(*, authoritative_status: AuthorityStatus,
                          manipulated: bool = False, duplicate: bool = False,
                          verified_copy: bool = False) -> OriginalityResult:
    if manipulated: return OriginalityResult.MANIPULATED
    if duplicate: return OriginalityResult.DUPLICATE
    if verified_copy: return OriginalityResult.VERIFIED_COPY
    if authoritative_status is AuthorityStatus.VERIFIED:
        return OriginalityResult.VERIFIED_ORIGINAL
    return OriginalityResult.UNABLE_TO_DETERMINE
