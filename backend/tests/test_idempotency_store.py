from app.idempotency import IdempotencyStore


def test_expired_entries_are_not_replayed():
    store = IdempotencyStore(ttl_seconds=1, max_items=10)
    store.put("key", "fingerprint", {"ok": True})
    store._items["key"] = store._items["key"].__class__(
        fingerprint="fingerprint",
        response={"ok": True},
        expires_at=0,
    )
    assert store.get("key", "fingerprint") is None


def test_store_bounds_entries_and_preserves_latest():
    store = IdempotencyStore(ttl_seconds=60, max_items=2)
    store.put("a", "a", {"n": 1})
    store.put("b", "b", {"n": 2})
    store.put("c", "c", {"n": 3})
    assert store.get("a", "a") is None
    assert store.get("b", "b") == {"n": 2}
    assert store.get("c", "c") == {"n": 3}


def test_same_key_different_fingerprint_still_conflicts():
    store = IdempotencyStore()
    store.put("key", "one", {"ok": True})
    try:
        store.get("key", "two")
    except ValueError as exc:
        assert "different request" in str(exc)
    else:
        raise AssertionError("expected fingerprint conflict")
