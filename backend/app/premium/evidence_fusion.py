"""Deterministic evidence fusion primitives.

This module intentionally does not declare a universal 'truth score'. It produces
an auditable aggregate from available signals while preserving uncertainty and
failed/unavailable checks. More advanced proprietary fusion can replace this
implementation behind the same interface.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..contracts import Evidence, SignalStatus


def fuse_image_evidence(signals: Sequence[Evidence]) -> tuple[str, float]:
    usable = [s for s in signals if s.status is SignalStatus.AVAILABLE and s.confidence is not None]
    if not usable:
        return "uncertain", 0.0

    weighted = sum(float(s.confidence) for s in usable) / len(usable)
    manipulation = sum(
        1 for s in usable if any(k in s.signal.lower() for k in ("tamper", "manipulation", "synthetic", "deepfake"))
    )
    if manipulation and weighted >= 0.80:
        return "likely_manipulated", round(weighted, 4)
    if weighted >= 0.80 and len(usable) >= 2:
        return "likely_authentic", round(weighted, 4)
    return "uncertain", round(weighted, 4)
