from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApiKeyPolicy:
    """Stable policy contract for future distributed API-key enforcement."""

    key_prefix: str = "rxk_"
    minimum_secret_bytes: int = 32
    default_scopes: tuple[str, ...] = ("verify:image", "receipt:verify")
    max_scopes_per_key: int = 16
    require_expiry_for_public_integrations: bool = True
    allow_bearer_auth: bool = True
    allow_header_auth: bool = True
    signing_keys_are_separate: bool = True
    support_key_rotation: bool = True
    support_emergency_revocation: bool = True
    support_per_key_rate_limits: bool = True
    support_usage_quotas: bool = True
    support_audit_events: bool = True
    support_anomaly_detection: bool = True
    support_agent_identity: bool = True
    support_crypto_agility: bool = True


API_KEY_POLICY = ApiKeyPolicy()
