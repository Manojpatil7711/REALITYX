from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .contracts import Evidence, SignalStatus


@dataclass(frozen=True)
class FusionDecision:
    result: str
    confidence: float
    evidence: list[Evidence]


def _usable(signals: list[Evidence]) -> list[Evidence]:
    return [
        signal for signal in signals
        if signal.status is SignalStatus.AVAILABLE
        and signal.confidence is not None
    ]


def fuse_evidence(signals: list[Evidence]) -> FusionDecision:
    """Conservative evidence fusion with explicit abstention."""
    usable = _usable(signals)
    if not usable:
        return FusionDecision("uncertain", 0.0, signals)

    positive = [s.confidence for s in usable if s.details.get("verdict") == "authentic"]
    negative = [
        s.confidence for s in usable
        if s.details.get("verdict") in {"manipulated", "ai_generated", "inauthentic"}
    ]

    if not positive and not negative:
        return FusionDecision("uncertain", 0.0, signals)

    p = sum(positive) / len(positive) if positive else 0.0
    n = sum(negative) / len(negative) if negative else 0.0
    support = max(p, n)
    agreement = 1.0 if not positive or not negative else max(0.0, 1.0 - abs(p - n))
    coverage = min(1.0, sqrt(len(usable) / 3.0))
    confidence = round(max(0.0, min(1.0, support * agreement * coverage)), 4)

    # Conflicting or weak evidence must abstain rather than overclaim.
    if positive and negative:
        return FusionDecision("uncertain", confidence, signals)
    if confidence < 0.70:
        return FusionDecision("uncertain", confidence, signals)
    if negative:
        return FusionDecision("inauthentic", confidence, signals)
    return FusionDecision("verified", confidence, signals)
