import io
from zipfile import ZipFile, ZIP_DEFLATED
import pytest

from app.batch_ingestion import validate_zip_archive


def make_zip(name: str, data: bytes = b"document") -> bytes:
    out = io.BytesIO()
    with ZipFile(out, "w", ZIP_DEFLATED) as z:
        z.writestr(name, data)
    return out.getvalue()


def test_valid_zip_returns_supported_documents():
    entries = validate_zip_archive(make_zip("customer-001/pan.pdf"))
    assert entries[0].relative_path == "customer-001/pan.pdf"
    assert entries[0].extension == "pdf"


def test_zip_traversal_rejected():
    with pytest.raises(ValueError, match="Path traversal"):
        validate_zip_archive(make_zip("../pan.pdf"))


def test_zip_absolute_path_rejected():
    with pytest.raises(ValueError, match="relative"):
        validate_zip_archive(make_zip("/pan.pdf"))


def test_zip_unsupported_only_rejected():
    with pytest.raises(ValueError, match="No supported"):
        validate_zip_archive(make_zip("note.txt"))


def test_zip_duplicate_paths_rejected():
    out = io.BytesIO()
    with ZipFile(out, "w", ZIP_DEFLATED) as z:
        z.writestr("pan.pdf", b"a")
        z.writestr("pan.pdf", b"b")
    with pytest.raises(ValueError, match="duplicate"):
        validate_zip_archive(out.getvalue())
