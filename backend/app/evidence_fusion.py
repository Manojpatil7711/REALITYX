from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .contracts import Evidence, EvidenceKind, SignalStatus, SignalVerdict, VerificationResult


@dataclass(frozen=True)
class FusionDecision:
    result: VerificationResult
    confidence: float
    evidence: list[Evidence]


def _usable(signals: list[Evidence]) -> list[Evidence]:
    return [
        signal
        for signal in signals
        if signal.status is SignalStatus.AVAILABLE
        and signal.confidence is not None
    ]


def _verdict_signals(signals: list[Evidence]) -> list[Evidence]:
    """Return only available evidence explicitly classified as verdict-bearing."""
    return [
        signal
        for signal in _usable(signals)
        if signal.kind is EvidenceKind.VERDICT and signal.verdict is not None
    ]


def fuse_evidence(signals: list[Evidence]) -> FusionDecision:
    """Fuse formal verdict-bearing signals; factual evidence never inflates confidence."""
    verdict_signals = _verdict_signals(signals)
    if not verdict_signals:
        return FusionDecision(VerificationResult.UNCERTAIN, 0.0, signals)

    positive = [
        s.confidence for s in verdict_signals
        if s.verdict in {SignalVerdict.AUTHENTIC, SignalVerdict.VERIFIED}
    ]
    negative = [
        s.confidence for s in verdict_signals
        if s.verdict in {
            SignalVerdict.MANIPULATED,
            SignalVerdict.AI_GENERATED,
            SignalVerdict.INAUTHENTIC,
        }
    ]

    p = sum(positive) / len(positive) if positive else 0.0
    n = sum(negative) / len(negative) if negative else 0.0
    support = max(p, n)
    agreement = 1.0 if not positive or not negative else max(0.0, 1.0 - abs(p - n))
    coverage = min(1.0, sqrt(len(verdict_signals) / 3.0))
    confidence = round(max(0.0, min(1.0, support * agreement * coverage)), 4)

    if positive and negative:
        return FusionDecision(VerificationResult.UNCERTAIN, confidence, signals)
    if confidence < 0.70:
        return FusionDecision(VerificationResult.UNCERTAIN, confidence, signals)
    if negative:
        return FusionDecision(VerificationResult.INAUTHENTIC, confidence, signals)
    return FusionDecision(VerificationResult.VERIFIED, confidence, signals)
