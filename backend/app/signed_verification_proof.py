"""Signed portable verification proofs and registry-backed trust checks.

Cryptographic validity and current trust are deliberately separate: a
historical proof can remain mathematically valid after its key is rotated,
expired, or revoked.
"""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from enum import StrEnum

from .trust_registry import KeyStatus, TrustRegistry
from .verification_proof import (
    VerificationProof,
    build_verification_proof,
    validate_verification_proof,
)

ALGORITHM = "Ed25519"
KEY_ID_ENV = "REALITYX_SIGNING_KEY_ID"
PRIVATE_KEY_ENV = "REALITYX_SIGNING_PRIVATE_KEY_B64"


@dataclass(frozen=True)
class SignedVerificationProof:
    proof: VerificationProof
    signature_algorithm: str
    signature: str


class SignedProofTrust(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    ROTATED = "rotated"
    REVOKED = "revoked"
    PROVIDER_REVOKED = "provider_revoked"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SignedProofVerification:
    cryptographically_valid: bool
    trusted_now: bool
    trust_status: SignedProofTrust
    key_id: str | None
    provider_id: str | None
    registry_digest: str


def _proof_bytes(proof: VerificationProof) -> bytes:
    return proof.proof_digest.encode("ascii")


def _key_id(signed: SignedVerificationProof) -> str | None:
    prefix = f"{ALGORITHM}:"
    if not signed.signature_algorithm.startswith(prefix):
        return None
    value = signed.signature_algorithm[len(prefix):].strip()
    return value or None


def sign_verification_proof(proof: VerificationProof) -> SignedVerificationProof:
    key_b64 = os.getenv(PRIVATE_KEY_ENV)
    key_id = os.getenv(KEY_ID_ENV)
    if not key_b64 or not key_id:
        raise RuntimeError("REALITYX signing credentials are not configured")
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        raw = base64.b64decode(key_b64, validate=True)
        private_key = Ed25519PrivateKey.from_private_bytes(raw)
        signature = private_key.sign(_proof_bytes(proof))
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Invalid REALITYX Ed25519 signing key") from exc
    return SignedVerificationProof(
        proof=proof,
        signature_algorithm=f"{ALGORITHM}:{key_id}",
        signature=base64.b64encode(signature).decode("ascii"),
    )


def _verify_signature(signed: SignedVerificationProof, public_key_b64: str) -> bool:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        public_key = Ed25519PublicKey.from_public_bytes(
            base64.b64decode(public_key_b64, validate=True)
        )
        public_key.verify(
            base64.b64decode(signed.signature, validate=True),
            _proof_bytes(signed.proof),
        )
        return True
    except Exception:
        return False


def verify_signed_proof(
    signed: SignedVerificationProof,
    registry: TrustRegistry,
) -> SignedProofVerification:
    key_id = _key_id(signed)
    digest = registry.digest()
    if not validate_verification_proof(signed.proof) or key_id is None:
        return SignedProofVerification(False, False, SignedProofTrust.UNKNOWN, key_id, None, digest)

    record = registry.get(key_id)
    if record is None:
        return SignedProofVerification(False, False, SignedProofTrust.UNKNOWN, key_id, None, digest)

    cryptographically_valid = _verify_signature(signed, record.key.public_key)
    provider_id = record.provider.provider_id

    if record.provider.trust.value == "revoked":
        status = SignedProofTrust.PROVIDER_REVOKED
    elif record.key.status is KeyStatus.REVOKED:
        status = SignedProofTrust.REVOKED
    elif record.key.status is KeyStatus.ROTATED:
        status = SignedProofTrust.ROTATED
    elif not registry.usable(key_id):
        status = SignedProofTrust.EXPIRED
    else:
        status = SignedProofTrust.ACTIVE

    return SignedProofVerification(
        cryptographically_valid,
        cryptographically_valid and status is SignedProofTrust.ACTIVE,
        status,
        key_id,
        provider_id,
        digest,
    )


def validate_signed_proof(signed: SignedVerificationProof) -> bool:
    """Legacy environment-backed validation kept for compatibility."""
    if not validate_verification_proof(signed.proof):
        return False
    key_b64 = os.getenv("REALITYX_SIGNING_PUBLIC_KEY_B64")
    if not key_b64:
        return False
    return _verify_signature(signed, key_b64)
