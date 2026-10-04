"""Provider trust registry with deterministic lifecycle and digest semantics.

This registry records provider/key metadata only. Listing or attesting a
provider never upgrades a verification decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json

from .ai_attestation import AIProvider, ProviderTrust

REGISTRY_VERSION = "2.0"


class KeyStatus(StrEnum):
    ACTIVE = "active"
    ROTATED = "rotated"
    REVOKED = "revoked"


@dataclass(frozen=True)
class ProviderKey:
    provider_id: str
    key_id: str
    public_key_fingerprint: str
    status: KeyStatus = KeyStatus.ACTIVE
    created_at: str = ""
    expires_at: str | None = None
    rotated_at: str | None = None
    revoked_at: str | None = None
    # Public verification material only; private keys are never stored here.
    public_key: str = ""


@dataclass(frozen=True)
class TrustRecord:
    provider: AIProvider
    key: ProviderKey
    registry_version: str = REGISTRY_VERSION


class TrustRegistry:
    def __init__(self) -> None:
        self._records: dict[str, TrustRecord] = {}

    def register(self, record: TrustRecord) -> None:
        if record.provider.trust is ProviderTrust.REVOKED:
            raise ValueError("revoked provider cannot register a key")
        if not record.key.key_id.strip():
            raise ValueError("key_id cannot be empty")
        existing = self._records.get(record.key.key_id)
        if existing is not None and existing != record:
            raise ValueError("key_id already registered with different metadata")
        self._records[record.key.key_id] = record

    def get(self, key_id: str) -> TrustRecord | None:
        return self._records.get(key_id)

    def usable(self, key_id: str, *, now: datetime | None = None) -> bool:
        record = self.get(key_id)
        if record is None:
            return False
        return key_usable(record, now=now)

    def digest(self) -> str:
        rows = [
            {
                "provider_id": record.provider.provider_id,
                "provider_version": record.provider.provider_version,
                "provider_trust": record.provider.trust.value,
                "key": {
                    "provider_id": record.key.provider_id,
                    "key_id": record.key.key_id,
                    "public_key_fingerprint": record.key.public_key_fingerprint,
                    "status": record.key.status.value,
                    "created_at": record.key.created_at,
                    "expires_at": record.key.expires_at,
                    "rotated_at": record.key.rotated_at,
                    "revoked_at": record.key.revoked_at,
                    "public_key": record.key.public_key,
                },
                "registry_version": record.registry_version,
            }
            for record in sorted(self._records.values(), key=lambda item: item.key.key_id)
        ]
        canonical = json.dumps(
            rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return sha256(canonical).hexdigest()


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("lifecycle timestamps must include timezone")
    return parsed.astimezone(timezone.utc)


def fingerprint_public_key(public_key: str) -> str:
    if not public_key.strip():
        raise ValueError("public key cannot be empty")
    return sha256(public_key.encode("utf-8")).hexdigest()


def register_key(
    provider: AIProvider,
    key_id: str,
    public_key: str,
    *,
    created_at: str = "",
    expires_at: str | None = None,
    public_key: str = "",
) -> TrustRecord:
    if provider.trust is ProviderTrust.REVOKED:
        raise ValueError("revoked provider cannot register a key")
    if not key_id.strip():
        raise ValueError("key_id cannot be empty")
    _parse_time(expires_at)
    key = ProviderKey(
        provider.provider_id,
        key_id,
        fingerprint_public_key(public_key),
        KeyStatus.ACTIVE,
        created_at,
        expires_at,
        None,
        None,
        public_key,
    )
    return TrustRecord(provider, key)


def key_usable(record: TrustRecord, *, now: datetime | None = None) -> bool:
    if record.provider.trust is ProviderTrust.REVOKED:
        return False
    if record.key.status is not KeyStatus.ACTIVE:
        return False
    current = now or datetime.now(timezone.utc)
    expiry = _parse_time(record.key.expires_at)
    return expiry is None or current < expiry
