import pytest

from app.contracts import VerificationArtifact, VerificationResult
from app.receipt_store import ReceiptStore


def _artifact(verification_id: str) -> VerificationArtifact:
    return VerificationArtifact(
        verification_id=verification_id,
        media_sha256="a" * 64,
        evidence_hash="b" * 64,
        result=VerificationResult.UNCERTAIN,
        confidence=0.0,
    )


def test_receipt_store_rejects_invalid_capacity():
    with pytest.raises(ValueError):
        ReceiptStore(max_items=0)


def test_receipt_store_is_bounded_fifo():
    store = ReceiptStore(max_items=2)
    store.put(_artifact("one"))
    store.put(_artifact("two"))
    store.put(_artifact("three"))

    assert store.get("one") is None
    assert store.get("two") is not None
    assert store.get("three") is not None


def test_receipt_store_returns_isolated_copy():
    store = ReceiptStore()
    artifact = _artifact("one")
    store.put(artifact)

    returned = store.get("one")
    assert returned is not None
    returned.result = VerificationResult.VERIFIED

    stored_again = store.get("one")
    assert stored_again is not None
    assert stored_again.result == VerificationResult.UNCERTAIN
