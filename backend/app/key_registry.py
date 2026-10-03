from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class PublicKeyRecord:
    key_id: str
    algorithm: str
    public_key: str
    status: str
    created_at: str
    retired_at: str | None = None
    revoked_at: str | None = None


class KeyRegistry:
    """Deployment-owned public-key registry; persistence can be swapped in later."""

    def __init__(self) -> None:
        self._keys: dict[str, PublicKeyRecord] = {}

    def register(self, record: PublicKeyRecord) -> None:
        if record.algorithm != "Ed25519":
            raise ValueError("Unsupported signing algorithm")
        if record.status not in {"active", "retired", "revoked"}:
            raise ValueError("Invalid key status")
        if record.status == "active":
            for existing in self._keys.values():
                if existing.algorithm == record.algorithm and existing.status == "active" and existing.key_id != record.key_id:
                    raise ValueError("Only one active Ed25519 key is allowed")
        self._keys[record.key_id] = record

    def get(self, key_id: str) -> PublicKeyRecord | None:
        return self._keys.get(key_id)

    def require_active(self, key_id: str) -> PublicKeyRecord:
        record = self.get(key_id)
        if record is None:
            raise RuntimeError("Signing key is not registered")
        if record.algorithm != "Ed25519" or record.status != "active":
            raise RuntimeError("Signing key is not active")
        return record

    def public_document(self) -> dict:
        return {
            "issuer": "REALITYX",
            "keys": [record.__dict__ for record in self._keys.values()],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


registry = KeyRegistry()


def load_env_key() -> None:
    """Load the deployment's public verification key without storing private material."""
    key_id = os.getenv("REALITYX_SIGNING_KEY_ID")
    public_key = os.getenv("REALITYX_SIGNING_PUBLIC_KEY_B64")
    if not key_id or not public_key:
        return
    try:
        raw = base64.b64decode(public_key, validate=True)
        if len(raw) != 32:
            raise ValueError("Ed25519 public key must be 32 bytes")
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Invalid REALITYX Ed25519 public key") from exc
    registry.register(PublicKeyRecord(
        key_id=key_id,
        algorithm="Ed25519",
        public_key=public_key,
        status="active",
        created_at=datetime.now(timezone.utc).isoformat(),
    ))
