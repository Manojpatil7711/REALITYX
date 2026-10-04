from app.batch_documents import DocumentKind
from app.document_classification import ClassificationConfidence, classify_document


def test_aadhaar_classification_uses_multiple_signals():
    result = classify_document(filename="customer-001.pdf", extracted_text="Aadhaar UIDAI")
    assert result.kind is DocumentKind.AADHAAR
    assert result.confidence is ClassificationConfidence.HIGH


def test_pan_classification_from_ocr_is_medium():
    result = classify_document(filename="scan-001.pdf", extracted_text="Permanent Account Number Income Tax Department")
    assert result.kind is DocumentKind.PAN
    assert result.confidence is ClassificationConfidence.MEDIUM


def test_ambiguous_document_abstains():
    result = classify_document(filename="customer.pdf", extracted_text="Aadhaar PAN")
    assert result.kind is DocumentKind.UNKNOWN


def test_unclassified_document_abstains():
    result = classify_document(filename="scan.pdf")
    assert result.kind is DocumentKind.UNKNOWN
    assert result.confidence is ClassificationConfidence.UNKNOWN
