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


_STRONG_PATTERNS = {
    DocumentKind.AADHAAR: ("aadhaar", "aadhar", "uidai", "unique identity"),
    DocumentKind.PAN: ("pan card", "pan", "income tax department", "permanent account number"),
    DocumentKind.PASSPORT: ("passport", "passport number", "travel document", "p<"),
    DocumentKind.VISA: ("visa", "entry permit", "residence visa", "visa number"),
    DocumentKind.DRIVER_LICENSE: ("driver license", "driving licence", "driving license"),
    DocumentKind.RESIDENCE_PERMIT: ("residence permit", "residency permit"),
    DocumentKind.NATIONAL_ID: ("national id", "identity card", "national identity"),
    DocumentKind.BANK_DOCUMENT: ("bank statement", "account statement", "passbook", "ifsc"),
}
_WEAK_PATTERNS = {DocumentKind.BANK_DOCUMENT: ("account number",)}


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
    sources = {item.source for item in evidence}
    confidence = (
        ClassificationConfidence.HIGH
        if len(sources) >= 2
        else ClassificationConfidence.MEDIUM
        if "ocr_text" in sources
        else ClassificationConfidence.LOW
    )
    return DocumentClassification(kind, confidence, tuple(evidence))
