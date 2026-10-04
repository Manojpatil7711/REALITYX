from app.pdf_ingestion import new_page_artifact, page_sha256


def test_page_hash_is_deterministic():
    assert page_sha256(b"page-1") == page_sha256(b"page-1")


def test_page_artifact_binds_source_and_page():
    result = new_page_artifact(
        source_document_id="doc-001",
        page_number=2,
        page_bytes=b"page-2",
    )
    assert result.source_document_id == "doc-001"
    assert result.page_number == 2
    assert len(result.page_sha256) == 64


def test_empty_page_is_rejected():
    try:
        page_sha256(b"")
    except ValueError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError("expected empty page rejection")


def test_invalid_page_number_is_rejected():
    try:
        new_page_artifact(
            source_document_id="doc-001",
            page_number=0,
            page_bytes=b"page",
        )
    except ValueError as exc:
        assert "page_number" in str(exc)
    else:
        raise AssertionError("expected page number rejection")
