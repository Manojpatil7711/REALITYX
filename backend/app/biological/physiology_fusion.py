from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PhysiologyEvidence:
    status: str
    confidence: float
    summary: str

def fuse_physiology_signals(signals: list[dict]) -> PhysiologyEvidence:
    available = [s for s in signals if s.get("status") == "available"]
    if not available:
        return PhysiologyEvidence(
            status="unavailable",
            confidence=0.0,
            summary="पुरेसा जैविक संकेत मिळाला नाही; त्यामुळे या माध्यमातून शारीरिक उपस्थितीबद्दल निष्कर्ष देता येत नाही.",
        )
    confidence = min(0.95, 0.35 + 0.15 * len(available))
    return PhysiologyEvidence(
        status="available",
        confidence=confidence,
        summary="उपलब्ध व्हिडिओ संकेतांमध्ये काही नैसर्गिक शारीरिक हालचालींची सुसंगती दिसते; हा वैद्यकीय निष्कर्ष नाही.",
    )
