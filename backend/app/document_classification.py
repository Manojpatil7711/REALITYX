"""Deterministic document classification for batch routing."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

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


_PATTERNS = {
    DocumentKind.AADHAAR: ("aadhaar", "aadhar", "uidai", "unique identity"),
    DocumentKind.PAN: ("pan card", "income tax department", "permanent account number"),
    DocumentKind.BANK_DOCUMENT: ("bank statement", "account statement", "passbook", "ifsc", "account number"),
}


def _hits(text: str, patterns: tuple[str, ...]) -> list[str]:
    value = text.casefold()
    return [item for item in patterns if item in value]


def classify_document(*, filename: str, extracted_text: str | None = None) -> DocumentClassification:
    """Route a document to downstream engines; never asserts authenticity."""
    candidates: dict[DocumentKind, list[ClassificationEvidence]] = {}
    for kind, patterns in _PATTERNS.items():
        hits = _hits(filename, patterns)
        if hits:
            candidates[kind] = [ClassificationEvidence("filename", hit) for hit in hits]
    if extracted_text:
        for kind, patterns in _PATTERNS.items():
            hits = _hits(extracted_text, patterns)
            if hits:
                candidates.setdefault(kind, []).extend(
                    ClassificationEvidence("ocr_text", hit) for hit in hits
                )
    if len(candidates) != 1:
        confidence = ClassificationConfidence.UNKNOWN if not candidates else ClassificationConfidence.LOW
        return DocumentClassification(DocumentKind.UNKNOWN, confidence, tuple(
            evidence for items in candidates.values() for evidence in items
        ))
    kind, evidence = next(iter(candidates.items()))
    sources = {item.source for item in evidence}
    confidence = ClassificationConfidence.HIGH if sources == {"filename", "ocr_text"} else (
        ClassificationConfidence.MEDIUM if "ocr_text" in sources else ClassificationConfidence.LOW
    )
    return DocumentClassification(kind, confidence, tuple(evidence))
