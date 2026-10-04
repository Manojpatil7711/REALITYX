import pytest

from app.ocr_contracts import OCRField, OCRStatus, OCRResult, unavailable_ocr, validate_ocr_confidence


def test_unavailable_ocr_preserves_reason():
    result = unavailable_ocr("provider not configured")
    assert result.status is OCRStatus.UNAVAILABLE
    assert result.limitations == ("provider not configured",)


def test_ocr_field_contract():
    field = OCRField(name="document_number", value="REDACTED", confidence=0.91, redacted=True)
    result = OCRResult(status=OCRStatus.AVAILABLE, fields=(field,), provider="provider-neutral")
    assert result.fields[0].redacted is True


def test_ocr_confidence_is_bounded():
    assert validate_ocr_confidence(0.98765) == 0.9877
    with pytest.raises(ValueError):
        validate_ocr_confidence(1.1)
