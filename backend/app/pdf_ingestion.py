"""Provider-neutral, bounded PDF page ingestion contracts.

Actual PDF decoding stays behind this adapter so the batch pipeline can add a
vetted PDF engine without coupling core verification logic to one vendor.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from enum import StrEnum


class PageExtractionStatus(StrEnum):
    READY = "ready"
    FAILED = "failed"


@dataclass(frozen=True)
class PDFPageArtifact:
    source_document_id: str
    page_number: int
    page_sha256: str
    media_type: str = "application/pdf-page"
    extraction_status: PageExtractionStatus = PageExtractionStatus.READY


def page_sha256(page_bytes: bytes) -> str:
    if not page_bytes:
        raise ValueError("page_bytes must not be empty")
    return hashlib.sha256(page_bytes).hexdigest()


def new_page_artifact(*, source_document_id: str, page_number: int, page_bytes: bytes) -> PDFPageArtifact:
    if not source_document_id.strip():
        raise ValueError("source_document_id must not be empty")
    if page_number < 1:
        raise ValueError("page_number must be >= 1")
    return PDFPageArtifact(
        source_document_id=source_document_id,
        page_number=page_number,
        page_sha256=page_sha256(page_bytes),
    )
