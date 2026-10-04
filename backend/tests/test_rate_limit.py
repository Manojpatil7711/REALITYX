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
