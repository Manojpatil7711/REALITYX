from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .contracts import Evidence, EvidenceKind, SignalStatus, SignalVerdict, VerificationResult
from .evidence_graph import EvidenceGraph


@dataclass(frozen=True)
class FusionDecision:
    result: VerificationResult
    confidence: float
    evidence: list[Evidence]
    independent_source_count: int = 0
    conflict: bool = False


def _verdict_signals(signals: list[Evidence]) -> list[Evidence]:
    return [
        signal for signal in signals
        if signal.status is SignalStatus.AVAILABLE
        and signal.kind is EvidenceKind.VERDICT
        and signal.verdict is not None
        and signal.confidence is not None
    ]


def fuse_evidence(signals: list[Evidence]) -> FusionDecision:
    verdict_signals = _verdict_signals(signals)
    if not verdict_signals:
        return FusionDecision(VerificationResult.UNCERTAIN, 0.0, signals)

    graph = EvidenceGraph.from_evidence(signals)
    groups = graph.independent_source_groups(verdict_signals)
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

    if conflict:
        # A conflict must remain visibly uncertain and cannot masquerade as
        # high-certainty proof merely because one side is numerically stronger.
        confidence = min(confidence, 0.49)
        return FusionDecision(VerificationResult.UNCERTAIN, confidence, signals, independent_count, True)
    if confidence < 0.70:
        return FusionDecision(VerificationResult.UNCERTAIN, confidence, signals, independent_count, False)
    if negative:
        return FusionDecision(VerificationResult.INAUTHENTIC, confidence, signals, independent_count, False)
    return FusionDecision(VerificationResult.VERIFIED, confidence, signals, independent_count, False)
