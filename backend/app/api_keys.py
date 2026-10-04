from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone

KEY_PREFIX = "rxk_"
KEY_BYTES = 32


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _digest(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ApiKeyRecord:
    key_id: str
    secret_digest: str
    scopes: frozenset[str]
    created_at: datetime
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    def active(self, now: datetime | None = None) -> bool:
        now = now or _utc_now()
        return self.revoked_at is None and (self.expires_at is None or self.expires_at > now)


class ApiKeyRegistry:
    """In-memory reference implementation; production storage must persist only digests."""

    def __init__(self) -> None:
        self._records: dict[str, ApiKeyRecord] = {}

    def issue(self, scopes: set[str], expires_at: datetime | None = None) -> tuple[str, ApiKeyRecord]:
        if not scopes:
            raise ValueError("At least one API scope is required")
        if expires_at is not None and expires_at <= _utc_now():
            raise ValueError("API key expiry must be in the future")
        key_id = secrets.token_urlsafe(18)
        secret = secrets.token_urlsafe(KEY_BYTES)
        token = f"{KEY_PREFIX}{key_id}.{secret}"
        record = ApiKeyRecord(key_id, _digest(secret), frozenset(scopes), _utc_now(), expires_at)
        self._records[key_id] = record
        return token, record

    def authenticate(self, token: str, required_scope: str) -> ApiKeyRecord | None:
        if not token.startswith(KEY_PREFIX) or "." not in token:
            return None
        key_id, secret = token[len(KEY_PREFIX):].split(".", 1)
        record = self._records.get(key_id)
        if record is None or not record.active() or required_scope not in record.scopes:
            return None
        supplied = _digest(secret)
        if not hmac.compare_digest(supplied, record.secret_digest):
            return None
        return record

    def revoke(self, key_id: str) -> bool:
        record = self._records.get(key_id)
        if record is None or record.revoked_at is not None:
            return False
        self._records[key_id] = ApiKeyRecord(
            key_id=record.key_id,
            secret_digest=record.secret_digest,
            scopes=record.scopes,
            created_at=record.created_at,
            expires_at=record.expires_at,
            revoked_at=_utc_now(),
        )
        return True


registry = ApiKeyRegistry()


PUBLIC_INTEGRATION_SCOPES = frozenset({"verify:image", "receipt:verify", "agent:trust"})


def validate_public_scopes(scopes: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """Normalize and fail closed on unknown public-integration scopes."""
    normalized = tuple(dict.fromkeys(scope.strip() for scope in scopes if scope.strip()))
    if not normalized:
        raise ValueError("At least one API key scope is required")
    if len(normalized) > 16:
        raise ValueError("Too many API key scopes")
    unknown = set(normalized) - PUBLIC_INTEGRATION_SCOPES
    if unknown:
        raise ValueError("Unsupported API key scope")
    return normalized
