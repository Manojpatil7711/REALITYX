from __future__ import annotations

import base64
import uuid

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import APIRouter, HTTPException

from .attestation import artifact_digest, canonical_json
from .key_registry import registry
from .receipt_store import store

router = APIRouter(prefix="/receipts")


@router.get("/{verification_id}")
def get_receipt(verification_id: str) -> dict:
    try:
        uuid.UUID(verification_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="verification_id must be a UUID") from exc

    artifact = store.get(verification_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Verification receipt not found")

    return {
        "receipt": artifact.model_dump(mode="json"),
        "receipt_digest": artifact_digest(artifact),
        "attested": artifact.signature is not None,
    }


@router.get("/{verification_id}/verify")
def verify_receipt(verification_id: str) -> dict:
    try:
        uuid.UUID(verification_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="verification_id must be a UUID") from exc

    artifact = store.get(verification_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Verification receipt not found")

    if not artifact.signature or not artifact.signature_algorithm:
        return {
            "verification_id": verification_id,
            "valid": False,
            "reason": "Receipt is not signed",
        }

    try:
        algorithm, key_id = artifact.signature_algorithm.split(":", 1)
    except ValueError:
        return {
            "verification_id": verification_id,
            "valid": False,
            "reason": "Invalid signature algorithm",
        }

    record = registry.get(key_id)
    if record is None or record.algorithm != algorithm or record.status != "active":
        return {
            "verification_id": verification_id,
            "valid": False,
            "reason": "Signing key is unavailable",
        }

    try:
        public_key = base64.b64decode(record.public_key, validate=True)
        signature = base64.b64decode(artifact.signature, validate=True)
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            signature,
            _unsigned_payload(artifact),
        )
    except (ValueError, TypeError, InvalidSignature):
        return {
            "verification_id": verification_id,
            "valid": False,
            "reason": "Signature verification failed",
        }

    return {
        "verification_id": verification_id,
        "valid": True,
        "algorithm": algorithm,
        "key_id": key_id,
        "receipt_digest": artifact_digest(artifact),
    }


def _unsigned_payload(artifact) -> bytes:
    unsigned = artifact.model_copy(update={"signature": None, "signature_algorithm": None})
    return canonical_json(
        unsigned.model_dump(
            mode="json",
            exclude={"signature", "signature_algorithm"},
        )
    )
