from app.batch_documents import (
    BatchJobStatus,
    CopyStatus,
    DocumentKind,
    document_fingerprint,
    new_batch_job,
)
from app.provenance import SourceConfidence, SourcePlatform, SourceProvenance, source_provenance_digest


def test_batch_job_starts_accepted():
    job = new_batch_job(3, owner_key_id="key-001")
    assert job.status is BatchJobStatus.ACCEPTED
    assert job.document_count == 3
    assert job.owner_key_id == "key-001"


def test_batch_job_requires_owner_key():
    import pytest
    with pytest.raises(ValueError, match="owner_key_id"):
        new_batch_job(3, owner_key_id=" ")


def test_document_fingerprint_is_deterministic():
    assert document_fingerprint("customer-001.pdf", 1234) == document_fingerprint("customer-001.pdf", 1234)


def test_copy_xerox_is_not_fake_verdict():
    assert CopyStatus.COPY_XEROX_INDICATED.value == "copy_xerox_indicated"
    assert DocumentKind.AADHAAR.value == "aadhaar"


def test_unknown_source_is_allowed_and_digest_is_stable():
    source = SourceProvenance(platform=SourcePlatform.UNKNOWN, confidence=SourceConfidence.UNKNOWN)
    assert source.source_url is None
    assert source.source_user_or_account is None
    assert source.original_creator_confirmed is False
    assert source_provenance_digest(source) == source_provenance_digest(source)
