from concurrent.futures import ThreadPoolExecutor

import pytest

from app.idempotency import IdempotencyStore


def test_claim_allows_only_one_concurrent_owner():
    store = IdempotencyStore()
    key = "same-key"
    fingerprint = "a" * 64

    def claim():
        return store.claim(key, fingerprint)

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda _: claim(), range(8)))

    assert sum(claimed for _, claimed in results) == 1
    assert sum(response is None for response, _ in results) == 8


def test_claim_replays_completed_response():
    store = IdempotencyStore()
    key = "same-key"
    fingerprint = "a" * 64
    response = {"result": "uncertain"}

    assert store.claim(key, fingerprint) == (None, True)
    store.put(key, fingerprint, response)

    assert store.claim(key, fingerprint) == (response, False)


def test_claim_rejects_fingerprint_reuse():
    store = IdempotencyStore()
    assert store.claim("same-key", "a" * 64) == (None, True)

    with pytest.raises(ValueError, match="different request"):
        store.claim("same-key", "b" * 64)


def test_release_allows_retry_after_failed_processing():
    store = IdempotencyStore()
    key = "same-key"
    fingerprint = "a" * 64

    assert store.claim(key, fingerprint) == (None, True)
    store.release(key, fingerprint)

    assert store.claim(key, fingerprint) == (None, True)
