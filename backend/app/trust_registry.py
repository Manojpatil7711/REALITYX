"""Global trust registry primitives for REALITYX.

The registry is a local policy boundary for provider keys and status. It does
not imply that a provider is globally trustworthy merely because it is listed.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from .ai_attestation import AIProvider, ProviderTrust

REGISTRY_VERSION = "1.0"

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

@dataclass(frozen=True)
class TrustRecord:
    provider: AIProvider
    key: ProviderKey
    registry_version: str = REGISTRY_VERSION

def fingerprint_public_key(public_key: str) -> str:
    if not public_key.strip():
        raise ValueError("public key cannot be empty")
    return sha256(public_key.encode("utf-8")).hexdigest()

def register_key(provider: AIProvider, key_id: str, public_key: str) -> TrustRecord:
    if provider.trust is ProviderTrust.REVOKED:
        raise ValueError("revoked provider cannot register a key")
    if not key_id.strip():
        raise ValueError("key_id cannot be empty")
    key = ProviderKey(provider.provider_id, key_id,
                      fingerprint_public_key(public_key))
    return TrustRecord(provider, key)

def key_usable(record: TrustRecord) -> bool:
    return (record.provider.trust is not ProviderTrust.REVOKED
            and record.key.status is KeyStatus.ACTIVE)
