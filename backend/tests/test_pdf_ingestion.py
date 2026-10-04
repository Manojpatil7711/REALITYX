from io import BytesIO

import pytest
from pypdf import PdfWriter

from app.pdf_ingestion import MAX_PDF_PAGES, separate_pdf_pages


def make_pdf(page_count: int) -> bytes:
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=200, height=200)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_separate_pdf_pages_returns_independent_page_artifacts():
    result = separate_pdf_pages(
        source_document_id="doc-001",
        pdf_bytes=make_pdf(3),
    )
    assert len(result) == 3
    assert [item.page_number for item in result] == [1, 2, 3]
    assert all(len(item.page_sha256) == 64 for item in result)
    assert all(item.source_document_id == "doc-001" for item in result)


def test_pdf_page_limit_is_enforced():
    with pytest.raises(ValueError, match="maximum page count"):
        separate_pdf_pages(
            source_document_id="doc-001",
            pdf_bytes=make_pdf(MAX_PDF_PAGES + 1),
        )
