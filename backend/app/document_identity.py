"""Privacy-conscious identity grouping for batch documents."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import os
import unicodedata


@dataclass(frozen=True)
class IdentitySignals:
    name: str | None = None
    date_of_birth: str | None = None
    document_number: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class IdentityMatch:
    matched: bool
    confidence: str
    reasons: tuple[str, ...] = ()


def _norm(value: str | None) -> str | None:
    if not value:
        return None
    value = unicodedata.normalize("NFKC", value).casefold()
    cleaned = " ".join(value.split())
    return cleaned or None


def pseudonymous_identity_key(signals: IdentitySignals, *, tenant_salt: bytes | None = None) -> str:
    """Non-reversible grouping key; not an authenticity proof.

    A tenant-specific secret salt is preferred in production so identical
    identity data cannot be correlated across tenants.
    """
    values = tuple(_norm(v) or "" for v in (
        signals.name, signals.date_of_birth, signals.document_number, signals.address
    ))
    if not any(values):
        raise ValueError("at least one identity signal is required")
    salt = tenant_salt
    if salt is None:
        configured = os.getenv("REALITYX_IDENTITY_HMAC_KEY")
        salt = configured.encode("utf-8") if configured else None
    payload = "|".join(values).encode("utf-8")
    if salt:
        return hmac.new(salt, payload, hashlib.sha256).hexdigest()
    return hashlib.sha256(payload).hexdigest()


def match_identity(left: IdentitySignals, right: IdentitySignals) -> IdentityMatch:
    strong = 0
    weak = 0
    reasons: list[str] = []
    for label, a, b in (
        ("name", left.name, right.name),
        ("date_of_birth", left.date_of_birth, right.date_of_birth),
        ("document_number", left.document_number, right.document_number),
        ("address", left.address, right.address),
    ):
        na, nb = _norm(a), _norm(b)
        if na and nb and na == nb:
            if label in {"date_of_birth", "document_number"}:
                strong += 1
            else:
                weak += 1
            reasons.append(label)

    if (left.document_number and right.document_number and _norm(left.document_number) != _norm(right.document_number)) or (
        left.date_of_birth and right.date_of_birth and _norm(left.date_of_birth) != _norm(right.date_of_birth)
    ):
        return IdentityMatch(False, "uncertain", ("conflicting_strong_identifier",))

    if strong >= 1 and weak >= 1:
        return IdentityMatch(True, "high", tuple(reasons))
    if strong >= 1 or weak >= 2:
        return IdentityMatch(True, "medium", tuple(reasons))
    return IdentityMatch(False, "uncertain", tuple(reasons))
