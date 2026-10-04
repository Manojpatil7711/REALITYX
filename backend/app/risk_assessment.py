"""Conservative cross-domain AI risk assessment.

Risk detection is separate from authenticity and legal identity decisions.
High-impact outcomes require independent evidence; uncertainty is preserved.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from .contracts import Evidence, EvidenceKind, SignalStatus


class RiskDomain(StrEnum):
    IDENTITY="identity"; DOCUMENT="document"; FINANCIAL="financial"
    GOVERNMENT="government"; SAFETY="safety"; MEDIA="media"
    AI_SYNTHETIC="ai_synthetic"; UNKNOWN="unknown"


class RiskLevel(StrEnum):
    NONE="none"; LOW="low"; ELEVATED="elevated"; HIGH="high"
    CRITICAL="critical"; UNCERTAIN="uncertain"


class RecommendedAction(StrEnum):
    ALLOW="allow"; REVIEW="human_review"; REVERIFY="reverify"
    BLOCK_PENDING_REVIEW="block_pending_review"


@dataclass(frozen=True)
class RiskAssessment:
    domain: RiskDomain
    level: RiskLevel
    confidence: float
    action: RecommendedAction
    reasons: tuple[str, ...]
    independent_sources: int


_HIGH_RISK_SIGNALS = {
    "identity_tamper", "document_tamper", "signature_invalid",
    "provenance_invalid", "ai_generated", "manipulation_detected",
    "credential_mismatch", "duplicate_identity_artifact",
}
_CRITICAL_SIGNALS = {
    "government_document_tamper", "financial_document_tamper",
    "safety_critical_media_tamper",
}


def assess_risk(evidence: list[Evidence], *,
                domain: RiskDomain = RiskDomain.UNKNOWN) -> RiskAssessment:
    available = [
        e for e in evidence
        if e.status is SignalStatus.AVAILABLE
        and e.kind in {EvidenceKind.FACT, EvidenceKind.VERDICT}
    ]
    if not available:
        return RiskAssessment(
            domain, RiskLevel.UNCERTAIN, 0.0, RecommendedAction.REVERIFY,
            ("No usable evidence was available.",), 0,
        )

    groups = {e.source_group or e.signal for e in available}
    critical = [
        e for e in available
        if e.signal in _CRITICAL_SIGNALS
        or e.details.get("risk_class") in _CRITICAL_SIGNALS
    ]
    high = [
        e for e in available
        if e.signal in _HIGH_RISK_SIGNALS
        or e.details.get("risk_class") in _HIGH_RISK_SIGNALS
    ]
    suspicious = [
        e for e in available
        if e.details.get("risk") in {"elevated", "high"}
        or e.details.get("tamper") is True
    ]

    if critical:
        level, action, selected = RiskLevel.CRITICAL, RecommendedAction.BLOCK_PENDING_REVIEW, critical
    elif high:
        level, action, selected = RiskLevel.HIGH, RecommendedAction.BLOCK_PENDING_REVIEW, high
    elif suspicious:
        level, action, selected = RiskLevel.ELEVATED, RecommendedAction.REVIEW, suspicious
    else:
        level, action, selected = RiskLevel.NONE, RecommendedAction.ALLOW, []

    confidences = [e.confidence for e in available if e.confidence is not None]
    confidence = min(1.0, sum(confidences) / len(confidences)) if confidences else 0.0

    # A single engine cannot create a high-impact decision.
    if level in {RiskLevel.HIGH, RiskLevel.CRITICAL} and len(groups) < 2:
        level, action = RiskLevel.UNCERTAIN, RecommendedAction.REVERIFY
        confidence = min(confidence, 0.49)

    reasons = tuple(f"{e.signal}: {e.summary}" for e in selected[:5])
    if not reasons:
        reasons = ("No material risk signal detected by available evidence.",)

    return RiskAssessment(
        domain, level, round(confidence, 4), action, reasons, len(groups)
    )
