"""Signed portable verification proofs for external systems."""
from __future__ import annotations
import base64
import os
from dataclasses import dataclass
from .verification_proof import VerificationProof, build_verification_proof, validate_verification_proof

ALGORITHM = "Ed25519"
KEY_ID_ENV = "REALITYX_SIGNING_KEY_ID"
PRIVATE_KEY_ENV = "REALITYX_SIGNING_PRIVATE_KEY_B64"

@dataclass(frozen=True)
class SignedVerificationProof:
    proof: VerificationProof
    signature_algorithm: str
    signature: str

def _proof_bytes(proof: VerificationProof) -> bytes:
    return proof.proof_digest.encode("ascii")

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

def validate_signed_proof(signed: SignedVerificationProof) -> bool:
    if not validate_verification_proof(signed.proof):
        return False
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key_b64 = os.getenv("REALITYX_SIGNING_PUBLIC_KEY_B64")
        if not key_b64:
            return False
        public_key = Ed25519PublicKey.from_public_bytes(
            base64.b64decode(key_b64, validate=True)
        )
        public_key.verify(
            base64.b64decode(signed.signature, validate=True),
            _proof_bytes(signed.proof),
        )
        return True
    except (ValueError, TypeError):
        return False
