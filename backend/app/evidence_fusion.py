from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .contracts import Evidence, SignalStatus, VerificationResult


@dataclass(frozen=True)
class FusionDecision:
    result: VerificationResult
    confidence: float
    evidence: list[Evidence]


_VERIFIED_VERDICTS = {VerificationResult.VERIFIED.value, "authentic"}
_INAUTHENTIC_VERDICTS = {
    "manipulated",
    "ai_generated",
    "inauthentic",
}
_VERDICT_VALUES = _VERIFIED_VERDICTS | _INAUTHENTIC_VERDICTS


def _usable(signals: list[Evidence]) -> list[Evidence]:
    return [
        signal
        for signal in signals
        if signal.status is SignalStatus.AVAILABLE
        and signal.confidence is not None
    ]


def _verdict_signals(signals: list[Evidence]) -> list[Evidence]:
    """Return only available signals that explicitly make a verdict claim."""
    return [
        signal
        for signal in _usable(signals)
        if signal.details.get("verdict") in _VERDICT_VALUES
    ]


def fuse_evidence(signals: list[Evidence]) -> FusionDecision:
    """Fuse explicit verdict-bearing signals; factual evidence never inflates confidence."""
    usable = _usable(signals)
    verdict_signals = _verdict_signals(usable)
    if not verdict_signals:
        return FusionDecision(VerificationResult.UNCERTAIN, 0.0, signals)

    positive = [
        s.confidence
        for s in verdict_signals
        if s.details.get("verdict") in _VERIFIED_VERDICTS
    ]
    negative = [
        s.confidence
        for s in verdict_signals
        if s.details.get("verdict") in _INAUTHENTIC_VERDICTS
    ]

    p = sum(positive) / len(positive) if positive else 0.0
    n = sum(negative) / len(negative) if negative else 0.0
    support = max(p, n)
    agreement = 1.0 if not positive or not negative else max(0.0, 1.0 - abs(p - n))

    # Coverage measures the number of independent verdict-bearing signals,
    # not the number of raw/factual signals in the pipeline.
    coverage = min(1.0, sqrt(len(verdict_signals) / 3.0))
    confidence = round(max(0.0, min(1.0, support * agreement * coverage)), 4)

    if positive and negative:
        return FusionDecision(VerificationResult.UNCERTAIN, confidence, signals)
    if confidence < 0.70:
        return FusionDecision(VerificationResult.UNCERTAIN, confidence, signals)
    if negative:
        return FusionDecision(VerificationResult.INAUTHENTIC, confidence, signals)
    return FusionDecision(VerificationResult.VERIFIED, confidence, signals)
