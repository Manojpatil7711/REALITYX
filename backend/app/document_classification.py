"""Deterministic document classification for batch routing."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .batch_documents import DocumentKind


class ClassificationConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ClassificationEvidence:
    source: str
    signal: str


@dataclass(frozen=True)
class DocumentClassification:
    kind: DocumentKind
    confidence: ClassificationConfidence
    evidence: tuple[ClassificationEvidence, ...] = ()


# Strong routing signals. Generic "account number" is weak evidence and cannot
# create a bank-document route by itself.
_STRONG_PATTERNS = {
    DocumentKind.AADHAAR: ("aadhaar", "aadhar", "uidai", "unique identity"),
    DocumentKind.PAN: ("pan card", "pan", "income tax department", "permanent account number"),
    DocumentKind.BANK_DOCUMENT: ("bank statement", "account statement", "passbook", "ifsc"),
}
_WEAK_PATTERNS = {
    DocumentKind.BANK_DOCUMENT: ("account number",),
}


def _hits(text: str, patterns: tuple[str, ...]) -> list[str]:
    value = text.casefold()
    return [item for item in patterns if re.search(rf"\b{re.escape(item)}\b", value)]


def classify_document(*, filename: str, extracted_text: str | None = None) -> DocumentClassification:
    """Route a document to downstream engines; never asserts authenticity."""
    candidates: dict[DocumentKind, list[ClassificationEvidence]] = {}

    for kind, patterns in _STRONG_PATTERNS.items():
        hits = _hits(filename, patterns)
        if hits:
            candidates[kind] = [ClassificationEvidence("filename", hit) for hit in hits]

    if extracted_text:
        for kind, patterns in _STRONG_PATTERNS.items():
            hits = _hits(extracted_text, patterns)
            if hits:
                candidates.setdefault(kind, []).extend(
                    ClassificationEvidence("ocr_text", hit) for hit in hits
                )

        # A generic account-number phrase only enriches an already strong
        # bank-document classification; it cannot create one.
        bank_strong = bool(_hits(extracted_text, _STRONG_PATTERNS[DocumentKind.BANK_DOCUMENT]))
        if bank_strong:
            candidates.setdefault(DocumentKind.BANK_DOCUMENT, []).extend(
                ClassificationEvidence("ocr_text", hit)
                for hit in _hits(extracted_text, _WEAK_PATTERNS[DocumentKind.BANK_DOCUMENT])
            )

    if len(candidates) != 1:
        confidence = ClassificationConfidence.UNKNOWN if not candidates else ClassificationConfidence.LOW
        return DocumentClassification(
            DocumentKind.UNKNOWN,
            confidence,
            tuple(evidence for items in candidates.values() for evidence in items),
        )

    kind, evidence = next(iter(candidates.items()))
    distinct_signals = {item.signal for item in evidence}
    sources = {item.source for item in evidence}
    if len(distinct_signals) >= 2:
        confidence = ClassificationConfidence.HIGH
    elif "ocr_text" in sources:
        confidence = ClassificationConfidence.MEDIUM
    else:
        confidence = ClassificationConfidence.LOW

    return DocumentClassification(kind, confidence, tuple(evidence))
