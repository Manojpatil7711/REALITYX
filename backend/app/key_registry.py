from __future__ import annotations

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
    """Small deployment-owned registry; production persistence can be swapped in."""

    def __init__(self) -> None:
        self._keys: dict[str, PublicKeyRecord] = {}

    def register(self, record: PublicKeyRecord) -> None:
        if record.algorithm != "Ed25519":
            raise ValueError("Unsupported signing algorithm")
        if record.status not in {"active", "retired", "revoked"}:
            raise ValueError("Invalid key status")
        self._keys[record.key_id] = record

    def get(self, key_id: str) -> PublicKeyRecord | None:
        return self._keys.get(key_id)

    def public_document(self) -> dict:
        return {
            "issuer": "REALITYX",
            "keys": [record.__dict__ for record in self._keys.values()],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


registry = KeyRegistry()
