"""Provider-neutral OCR contracts with explicit uncertainty."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OCRStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


@dataclass(frozen=True)
class OCRField:
    name: str
    value: str
    confidence: float
    redacted: bool = False


@dataclass(frozen=True)
class OCRResult:
    status: OCRStatus
    text: str = ""
    fields: tuple[OCRField, ...] = ()
    provider: str = "none"
    limitations: tuple[str, ...] = ()


def unavailable_ocr(reason: str) -> OCRResult:
    if not reason.strip():
        raise ValueError("reason must not be empty")
    return OCRResult(status=OCRStatus.UNAVAILABLE, limitations=(reason,))


def validate_ocr_confidence(value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError("OCR confidence must be between 0 and 1")
    return round(value, 4)
