from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfWriter

from app.batch_pipeline import (
    PipelineDocument,
    build_batch_pipeline_report,
)
from app.document_identity import IdentitySignals


@dataclass
class StubOCR:
    text_by_media_type: dict[str, str]

    def extract_text(self, *, data: bytes, media_type: str) -> str:
        return self.text_by_media_type.get(media_type, "")


def _pdf_bytes() -> bytes:
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=400)
    writer.write(output)
    return output.getvalue()


def test_groups_aadhaar_and_pan_into_separate_report_slots() -> None:
    ocr = StubOCR({})
    documents = [
        PipelineDocument(
            document_id="aadhaar-1",
            filename="aadhaar.pdf",
            data=_pdf_bytes(),
            media_type="application/pdf",
            identity=IdentitySignals(name="Ravi Patil", date_of_birth="1990-01-01"),
        ),
        PipelineDocument(
            document_id="pan-1",
            filename="pan.pdf",
            data=_pdf_bytes(),
            media_type="application/pdf",
            identity=IdentitySignals(name="Ravi Patil", date_of_birth="1990-01-01"),
        ),
    ]

    report = build_batch_pipeline_report(documents, ocr=ocr)

    assert report.document_count == 2
    assert len(report.customers) == 1
    customer = report.customers[0]
    assert customer.aadhaar is not None
    assert customer.pan is not None
    assert customer.aadhaar.document.kind.value == "aadhaar"
    assert customer.pan.document.kind.value == "pan"
    assert len(customer.aadhaar.pages) == 1
    assert len(customer.pan.pages) == 1


def test_conflicting_dob_keeps_documents_separate() -> None:
    ocr = StubOCR({})
    documents = [
        PipelineDocument(
            document_id="a",
            filename="aadhaar.pdf",
            data=_pdf_bytes(),
            media_type="application/pdf",
            identity=IdentitySignals(name="Ravi Patil", date_of_birth="1990-01-01"),
        ),
        PipelineDocument(
            document_id="b",
            filename="pan.pdf",
            data=_pdf_bytes(),
            media_type="application/pdf",
            identity=IdentitySignals(name="Ravi Patil", date_of_birth="1991-01-01"),
        ),
    ]

    report = build_batch_pipeline_report(documents, ocr=ocr)
    assert len(report.customers) == 2
