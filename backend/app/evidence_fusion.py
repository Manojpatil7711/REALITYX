from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .contracts import Evidence, EvidenceKind, SignalStatus, SignalVerdict, VerificationResult
from .evidence_graph import EvidenceGraph


def _safe_evidence_graph_digest(signals: list[Evidence]) -> str:
    """Return the deterministic evidence digest even when provenance is malformed."""
    if not signals:
        return ""
    try:
        return EvidenceGraph.from_evidence(signals).digest()
    except ValueError:
        # The digest is an artifact identity for the evidence set, not a claim
        # that the provenance graph is valid. Keep it available for abstention.
        return EvidenceGraph.digest_evidence(signals)


@dataclass(frozen=True)
class FusionDecision:
    result: VerificationResult
    confidence: float
    evidence: list[Evidence]
    independent_source_count: int = 0
    conflict: bool = False
    evidence_graph_digest: str = ""


def _verdict_signals(signals: list[Evidence]) -> list[Evidence]:
    return [
        signal for signal in signals
        if signal.status is SignalStatus.AVAILABLE
        and signal.kind is EvidenceKind.VERDICT
        and signal.verdict is not None
        and signal.confidence is not None
    ]


def _c2pa_integrity_conflict(signals: list[Evidence]) -> bool:
    """C2PA is provenance evidence, but explicit invalid/conflicting state is security-relevant."""
    for signal in signals:
        if not signal.evidence_id.startswith("c2pa:"):
            continue
        status = str(signal.details.get("credential_status", "")).lower()
        if status in {"invalid", "conflicting"} or signal.status is SignalStatus.FAILED:
            return True
    return False


def fuse_evidence(signals: list[Evidence]) -> FusionDecision:
    c2pa_conflict = _c2pa_integrity_conflict(signals)
    verdict_signals = _verdict_signals(signals)
    if not verdict_signals:
        return FusionDecision(
            VerificationResult.UNCERTAIN,
            0.0,
            signals,
            conflict=c2pa_conflict,
            evidence_graph_digest=_safe_evidence_graph_digest(signals),
        )

    # Provenance is security-critical input. A malformed graph must never turn
    # an untrusted upload into a 500 or an implicit positive/negative verdict.
    try:
        graph = EvidenceGraph.from_evidence(signals)
        groups = graph.independent_source_groups(verdict_signals)
    except ValueError:
        return FusionDecision(
            VerificationResult.UNCERTAIN,
            0.0,
            signals,
            independent_source_count=0,
            conflict=False,
            evidence_graph_digest=_safe_evidence_graph_digest(signals),
        )

    independent_count = len(groups)

    positive = [s.confidence for s in verdict_signals if s.verdict in {SignalVerdict.AUTHENTIC, SignalVerdict.VERIFIED}]
    negative = [s.confidence for s in verdict_signals if s.verdict in {SignalVerdict.MANIPULATED, SignalVerdict.AI_GENERATED, SignalVerdict.INAUTHENTIC}]

    p = sum(positive) / len(positive) if positive else 0.0
    n = sum(negative) / len(negative) if negative else 0.0
    support = max(p, n)
    conflict = bool(positive and negative)
    agreement = 1.0 if not conflict else max(0.0, 1.0 - abs(p - n))

    # Correlated signals do not create additional independent support.
    coverage = min(1.0, sqrt(independent_count / 3.0))
    confidence = round(max(0.0, min(1.0, support * agreement * coverage)), 4)

    if conflict or c2pa_conflict:
        # Provenance conflicts remain visibly uncertain and never create a verdict.
        confidence = min(confidence, 0.49)
        return FusionDecision(
            VerificationResult.UNCERTAIN,
            confidence,
            signals,
            independent_count,
            True,
            graph.digest(),
        )
    if confidence < 0.70:
        return FusionDecision(VerificationResult.UNCERTAIN, confidence, signals, independent_count, False, graph.digest())
    if negative:
        return FusionDecision(VerificationResult.INAUTHENTIC, confidence, signals, independent_count, False, graph.digest())
    return FusionDecision(VerificationResult.VERIFIED, confidence, signals, independent_count, False, graph.digest())
