"""Bounded PDF page separation for enterprise batch ingestion."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from enum import StrEnum
from io import BytesIO

from pypdf import PdfReader


MAX_PDF_PAGES = 500
MAX_PDF_BYTES = 25 * 1024 * 1024


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


def extract_pdf_pages(*, source_document_id: str, pdf_bytes: bytes) -> tuple[tuple[PDFPageArtifact, bytes], ...]:
    """Split a bounded PDF into deterministic page artifacts and page bytes."""
    if not source_document_id.strip():
        raise ValueError("source_document_id must not be empty")
    if not pdf_bytes:
        raise ValueError("pdf_bytes must not be empty")
    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise ValueError("pdf exceeds maximum size")

    reader = PdfReader(BytesIO(pdf_bytes), strict=False)
    if len(reader.pages) > MAX_PDF_PAGES:
        raise ValueError("pdf exceeds maximum page count")

    artifacts: list[tuple[PDFPageArtifact, bytes]] = []
    for index, page in enumerate(reader.pages, start=1):
        output = BytesIO()
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_page(page)
        writer.write(output)
        serialized = output.getvalue()
        artifacts.append(
            (
                new_page_artifact(
                    source_document_id=source_document_id,
                    page_number=index,
                    page_bytes=serialized,
                ),
                serialized,
            )
        )
    return tuple(artifacts)


def separate_pdf_pages(*, source_document_id: str, pdf_bytes: bytes) -> tuple[PDFPageArtifact, ...]:
    """Split a bounded PDF into independently addressable page artifacts."""
    return tuple(
        artifact
        for artifact, _page_bytes in extract_pdf_pages(
            source_document_id=source_document_id,
            pdf_bytes=pdf_bytes,
        )
    )
