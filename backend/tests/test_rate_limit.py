from app.rate_limit import FixedWindowRateLimiter


def test_fixed_window_rejects_after_limit():
    limiter = FixedWindowRateLimiter(limit=2, window_seconds=60)

    assert limiter.check("client", now=100.0).allowed
    assert limiter.check("client", now=101.0).allowed

    blocked = limiter.check("client", now=102.0)
    assert not blocked.allowed
    assert blocked.retry_after_seconds == 58


def test_fixed_window_resets_after_window():
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=60)

    assert limiter.check("client", now=100.0).allowed
    assert not limiter.check("client", now=159.0).allowed
    assert limiter.check("client", now=160.0).allowed


def test_fixed_window_isolates_identities():
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=60)

    assert limiter.check("client-a", now=100.0).allowed
    assert not limiter.check("client-a", now=101.0).allowed
    assert limiter.check("client-b", now=101.0).allowed


def test_fixed_window_prunes_expired_identity_state():
    limiter = FixedWindowRateLimiter(limit=1, window_seconds=60, max_identities=2)
    assert limiter.check("client-a", now=100.0).allowed
    assert limiter.check("client-b", now=100.0).allowed
    assert limiter.check("client-c", now=161.0).allowed
    assert len(limiter._windows) == 1


def test_fixed_window_rejects_invalid_capacity():
    import pytest
    with pytest.raises(ValueError):
        FixedWindowRateLimiter(limit=1, window_seconds=60, max_identities=0)


def test_privacy_rate_limit_identity_is_deterministic_and_scoped():
    from app.rate_limit import privacy_rate_limit_identity
    first = privacy_rate_limit_identity("agent-key", "key-a", "127.0.0.1")
    assert first == privacy_rate_limit_identity("agent-key", "key-a", "127.0.0.1")
    assert first != privacy_rate_limit_identity("agent-key", "key-b", "127.0.0.1")
    assert first != privacy_rate_limit_identity("receipt", "key-a", "127.0.0.1")
    assert len(first) == 64


def test_privacy_rate_limit_identity_fails_closed_on_missing_principal():
    import pytest
    with pytest.raises(ValueError):
        privacy_rate_limit_identity("agent-key", "")
