from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json


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
        if not record.key_id or ":" in record.key_id:
            raise ValueError("Invalid key id")
        if record.status == "active":
            for existing in self._keys.values():
                if existing.algorithm == record.algorithm and existing.status == "active" and existing.key_id != record.key_id:
                    raise ValueError("Only one active Ed25519 key is allowed")
        try:
            raw = base64.b64decode(record.public_key, validate=True)
        except (ValueError, TypeError) as exc:
            raise ValueError("Invalid Ed25519 public key encoding") from exc
        if len(raw) != 32:
            raise ValueError("Ed25519 public key must be 32 bytes")
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
        """Return a stable public trust document containing active keys only."""
        keys = [
            {
                "key_id": record.key_id,
                "algorithm": record.algorithm,
                "public_key": record.public_key,
                "status": record.status,
                "created_at": record.created_at,
                "retired_at": record.retired_at,
                "revoked_at": record.revoked_at,
            }
            for record in sorted(self._keys.values(), key=lambda item: item.key_id)
            if record.status == "active"
        ]
        return {"issuer": "REALITYX", "document_version": "1.0", "keys": keys}

    def public_document_digest(self) -> str:
        """Return a deterministic digest suitable for trust receipts/audits."""
        canonical = json.dumps(
            self.public_document(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return sha256(canonical).hexdigest()


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
