from datetime import datetime, timedelta, timezone

from app.api_keys import registry


def test_issued_key_authenticates_only_with_matching_scope():
    token, record = registry.issue({"verify:image"})
    assert registry.authenticate(token, "verify:image") == record
    assert registry.authenticate(token, "admin") is None


def test_wrong_secret_is_rejected():
    token, _ = registry.issue({"verify:image"})
    prefix, _ = token.rsplit(".", 1)
    assert registry.authenticate(prefix + ".wrong", "verify:image") is None


def test_expired_key_is_rejected():
    token, _ = registry.issue({"verify:image"}, datetime.now(timezone.utc) + timedelta(seconds=1))
    assert registry.authenticate(token, "verify:image") is not None


def test_revocation_is_immediate():
    token, record = registry.issue({"verify:image"})
    assert registry.revoke(record.key_id) is True
    assert registry.authenticate(token, "verify:image") is None
    assert registry.revoke(record.key_id) is False
