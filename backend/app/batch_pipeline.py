"""Deterministic PDF/OCR/classification/identity pipeline for enterprise batches.

This module orchestrates stages but never treats OCR or classification as
authenticity proof. Real OCR engines are injected through a small provider
protocol so paid/external infrastructure remains optional.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .batch_documents import (
    BatchCustomer,
    BatchDocumentResult,
    DocumentKind,
    CopyStatus,
)
from .document_classification import (
    ClassificationConfidence,
    classify_document,
)
from .document_identity import IdentityGroup, IdentitySignals, group_document_identities
from .pdf_ingestion import PDFPageArtifact, separate_pdf_pages


class OCRProvider(Protocol):
    """Provider-neutral OCR boundary; implementations may be local or external."""

    def extract_text(self, *, data: bytes, media_type: str) -> str:
        ...


@dataclass(frozen=True)
class OCRPageResult:
    page_number: int
    text: str
    provider: str = "unknown"


@dataclass(frozen=True)
class PipelineDocument:
    document_id: str
    filename: str
    data: bytes
    media_type: str
    identity: IdentitySignals = IdentitySignals()
    copy_status: CopyStatus = CopyStatus.UNDETERMINED


@dataclass(frozen=True)
class PipelineDocumentResult:
    document: BatchDocumentResult
    classification_confidence: ClassificationConfidence
    classification_evidence: tuple[str, ...]
    pages: tuple[PDFPageArtifact, ...] = ()
    ocr_pages: tuple[OCRPageResult, ...] = ()


@dataclass(frozen=True)
class CustomerReport:
    customer_id: str
    aadhaar: PipelineDocumentResult | None = None
    pan: PipelineDocumentResult | None = None
    documents: tuple[PipelineDocumentResult, ...] = ()


@dataclass(frozen=True)
class BatchPipelineReport:
    customers: tuple[CustomerReport, ...]
    document_count: int
    limitations: tuple[str, ...] = ()


def _ocr_pages(
    item: PipelineDocument,
    *,
    ocr: OCRProvider,
) -> tuple[tuple[PDFPageArtifact, ...], tuple[OCRPageResult, ...]]:
    if item.media_type == "application/pdf":
        pages = separate_pdf_pages(
            source_document_id=item.document_id,
            pdf_bytes=item.data,
        )
        texts = tuple(
            OCRPageResult(
                page_number=page.page_number,
                text=ocr.extract_text(data=item.data, media_type=item.media_type),
            )
            for page in pages
        )
        return pages, texts

    text = ocr.extract_text(data=item.data, media_type=item.media_type)
    return (), (OCRPageResult(page_number=1, text=text),)


def build_batch_pipeline_report(
    documents: list[PipelineDocument],
    *,
    ocr: OCRProvider,
) -> BatchPipelineReport:
    """Run bounded ingestion -> OCR -> classification -> identity grouping.

    The output is a routing/report object. It deliberately does not produce an
    authenticity verdict; forensic verification remains a separate evidence
    stage. Ambiguous identity links remain separate.
    """
    if not documents:
        raise ValueError("documents must not be empty")
    if len(documents) > 10_000:
        raise ValueError("too many documents")

    results: dict[str, PipelineDocumentResult] = {}
    identities: list[tuple[str, IdentitySignals]] = []

    for item in documents:
        if not item.document_id.strip():
            raise ValueError("document_id must not be empty")
        pages, ocr_pages = _ocr_pages(item, ocr=ocr)
        extracted_text = "\n".join(page.text for page in ocr_pages).strip() or None
        classification = classify_document(
            filename=item.filename,
            extracted_text=extracted_text,
        )
        result = BatchDocumentResult(
            document_id=item.document_id,
            customer_id="",
            filename=item.filename,
            kind=classification.kind,
            copy_status=item.copy_status,
            limitations=(
                ("classification_uncertain",)
                if classification.confidence in {
                    ClassificationConfidence.UNKNOWN,
                    ClassificationConfidence.LOW,
                }
                else (),
            ),
        )
        results[item.document_id] = PipelineDocumentResult(
            document=result,
            classification_confidence=classification.confidence,
            classification_evidence=tuple(
                f"{e.source}:{e.signal}" for e in classification.evidence
            ),
            pages=pages,
            ocr_pages=ocr_pages,
        )
        identities.append((item.document_id, item.identity))

    groups: tuple[IdentityGroup, ...] = group_document_identities(identities)
    customers: list[CustomerReport] = []

    for group in groups:
        group_results = tuple(
            PipelineDocumentResult(
                document=PipelineDocumentResultRef.document_with_customer(
                    results[document_id].document,
                    group.group_id,
                ),
                classification_confidence=results[document_id].classification_confidence,
                classification_evidence=results[document_id].classification_evidence,
                pages=results[document_id].pages,
                ocr_pages=results[document_id].ocr_pages,
            )
            for document_id in group.document_ids
        )
        aadhaar = next(
            (item for item in group_results if item.document.kind is DocumentKind.AADHAAR),
            None,
        )
        pan = next(
            (item for item in group_results if item.document.kind is DocumentKind.PAN),
            None,
        )
        customers.append(
            CustomerReport(
                customer_id=group.group_id,
                aadhaar=aadhaar,
                pan=pan,
                documents=group_results,
            )
        )

    return BatchPipelineReport(
        customers=tuple(customers),
        document_count=len(documents),
        limitations=(
            "OCR provider output is routing evidence only; authenticity requires forensic evidence fusion.",
            "Official authority verification is not assumed unless a trusted provider is explicitly connected.",
            "Original physical document status cannot be proven from a scan alone.",
        ),
    )


class PipelineDocumentResultRef:
    """Internal immutable helper to avoid mutating result objects."""

    @staticmethod
    def document_with_customer(
        document: BatchDocumentResult,
        customer_id: str,
    ) -> BatchDocumentResult:
        return BatchDocumentResult(
            document_id=document.document_id,
            customer_id=customer_id,
            filename=document.filename,
            kind=document.kind,
            copy_status=document.copy_status,
            verification_status=document.verification_status,
            verification_id=document.verification_id,
            evidence_ids=document.evidence_ids,
            limitations=document.limitations,
        )
