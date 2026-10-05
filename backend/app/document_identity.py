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
    # Provider-supplied opaque token; REALITYX never interprets or displays its value.
    opaque_identity_key: str | None = None


@dataclass(frozen=True)
class IdentityMatch:
    matched: bool
    confidence: str
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class IdentityGroup:
    group_id: str
    document_ids: tuple[str, ...]


def _norm(value: str | None) -> str | None:
    if not value:
        return None
    value = unicodedata.normalize("NFKC", value).casefold()
    cleaned = " ".join(value.split())
    return cleaned or None


def pseudonymous_identity_key(signals: IdentitySignals, *, tenant_salt: bytes | None = None) -> str:
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
    opaque_left = _norm(left.opaque_identity_key)
    opaque_right = _norm(right.opaque_identity_key)
    if opaque_left and opaque_right and opaque_left == opaque_right:
        strong += 1
        reasons.append("opaque_identity_match")

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


def group_document_identities(
    documents: list[tuple[str, IdentitySignals]],
) -> tuple[IdentityGroup, ...]:
    """Group only when evidence supports the same person; ambiguous links stay separate."""
    if len(documents) > 10_000:
        raise ValueError("too many documents")
    groups: list[list[str]] = []
    signals_by_id = dict(documents)
    for document_id, signals in documents:
        placed = False
        for group in groups:
            candidates = [signals_by_id[item] for item in group]
            matches = [match_identity(signals, candidate) for candidate in candidates]
            if any(match.matched and match.confidence in {"high", "medium"} for match in matches):
                group.append(document_id)
                placed = True
                break
        if not placed:
            groups.append([document_id])
    return tuple(
        IdentityGroup(
            group_id=hashlib.sha256("|".join(sorted(group)).encode("utf-8")).hexdigest()[:24],
            document_ids=tuple(group),
        )
        for group in groups
    )
