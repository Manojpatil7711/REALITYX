"""Public REALITYX identity and ownership-proof boundary.

This module separates branding from factual ownership verification. A public
identity document may describe the operator, domain and verification status,
but it never claims ownership verification unless an explicit server-side
verification status is configured.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
import os


IDENTITY_PROTOCOL_VERSION = "1.0"


class OwnershipStatus(StrEnum):
    UNVERIFIED = "unverified"
    DOMAIN_VERIFIED = "domain_verified"
    OWNER_VERIFIED = "owner_verified"


@dataclass(frozen=True)
class SiteIdentity:
    product: str
    tagline: str
    operator: str
    domain: str
    ownership_status: OwnershipStatus
    verification_method: str
    identity_version: str = IDENTITY_PROTOCOL_VERSION

    def public_document(self) -> dict[str, str]:
        return {
            "product": self.product,
            "tagline": self.tagline,
            "operator": self.operator,
            "domain": self.domain,
            "ownership_status": self.ownership_status.value,
            "verification_method": self.verification_method,
            "identity_version": self.identity_version,
        }


def _status(value: str) -> OwnershipStatus:
    try:
        return OwnershipStatus(value.strip().lower())
    except ValueError:
        return OwnershipStatus.UNVERIFIED


def load_site_identity() -> SiteIdentity:
    return SiteIdentity(
        product=os.getenv("REALITYX_PRODUCT_NAME", "REALITYX"),
        tagline=os.getenv("REALITYX_TAGLINE", "VERIFY WHAT'S REAL."),
        operator=os.getenv("REALITYX_OWNER_DISPLAY_NAME", "REALITYX operator"),
        domain=os.getenv("REALITYX_SITE_DOMAIN", ""),
        ownership_status=_status(
            os.getenv("REALITYX_OWNERSHIP_STATUS", OwnershipStatus.UNVERIFIED.value)
        ),
        verification_method=os.getenv(
            "REALITYX_OWNERSHIP_METHOD",
            "not configured; ownership must be independently verified",
        ),
    )


def identity_digest(identity: SiteIdentity) -> str:
    payload = json.dumps(
        identity.public_document(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
