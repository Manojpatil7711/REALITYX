import base64

import pytest

from app.key_registry import KeyRegistry, PublicKeyRecord


def _record(key_id: str = "key-1", status: str = "active") -> PublicKeyRecord:
    return PublicKeyRecord(
        key_id=key_id,
        algorithm="Ed25519",
        public_key=base64.b64encode(b"x" * 32).decode(),
        status=status,
        created_at="now",
    )


def test_registry_rejects_invalid_key_id():
    registry = KeyRegistry()
    with pytest.raises(ValueError, match="Invalid key id"):
        registry.register(_record(":bad"))


def test_registry_rejects_invalid_public_key():
    registry = KeyRegistry()
    with pytest.raises(ValueError, match="32 bytes"):
        registry.register(PublicKeyRecord("key-1", "Ed25519", base64.b64encode(b"short").decode(), "active", "now"))


def test_registry_allows_only_one_active_key():
    registry = KeyRegistry()
    registry.register(_record("key-1"))
    with pytest.raises(ValueError, match="Only one active"):
        registry.register(_record("key-2"))


def test_public_document_exposes_only_active_keys():
    registry = KeyRegistry()
    registry.register(_record("active", "active"))
    registry.register(_record("retired", "retired"))
    registry.register(_record("revoked", "revoked"))
    keys = registry.public_document()["keys"]
    assert [item["key_id"] for item in keys] == ["active"]


def test_require_active_rejects_retired_and_revoked():
    registry = KeyRegistry()
    registry.register(_record("retired", "retired"))
    registry.register(_record("revoked", "revoked"))
    with pytest.raises(RuntimeError, match="not active"):
        registry.require_active("retired")
    with pytest.raises(RuntimeError, match="not active"):
        registry.require_active("revoked")
