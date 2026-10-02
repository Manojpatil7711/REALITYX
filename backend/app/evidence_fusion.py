from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .contracts import Evidence, SignalStatus, VerificationResult


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


def fuse_evidence(signals: list[Evidence]) -> FusionDecision:
    """Fuse only explicit verdict-bearing signals; facts alone never create a verdict."""
    usable = _usable(signals)
    if not usable:
        return FusionDecision(VerificationResult.UNCERTAIN, 0.0, signals)

    positive = [
        s.confidence
        for s in usable
        if s.details.get("verdict") in {VerificationResult.VERIFIED.value, "authentic"}
    ]
    negative = [
        s.confidence
        for s in usable
        if s.details.get("verdict") in {"manipulated", "ai_generated", "inauthentic"}
    ]

    if not positive and not negative:
        return FusionDecision(VerificationResult.UNCERTAIN, 0.0, signals)

    p = sum(positive) / len(positive) if positive else 0.0
    n = sum(negative) / len(negative) if negative else 0.0
    support = max(p, n)
    agreement = 1.0 if not positive or not negative else max(0.0, 1.0 - abs(p - n))
    coverage = min(1.0, sqrt(len(usable) / 3.0))
    confidence = round(max(0.0, min(1.0, support * agreement * coverage)), 4)

    if positive and negative:
        return FusionDecision(VerificationResult.UNCERTAIN, confidence, signals)
    if confidence < 0.70:
        return FusionDecision(VerificationResult.UNCERTAIN, confidence, signals)
    if negative:
        return FusionDecision(VerificationResult.INAUTHENTIC, confidence, signals)
    return FusionDecision(VerificationResult.VERIFIED, confidence, signals)
