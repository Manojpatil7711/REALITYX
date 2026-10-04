from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Request

from .attestation import artifact_digest, verify_artifact_signature
from .rate_limit import receipt_read_limiter, receipt_verify_limiter
from .receipt_store import store

router = APIRouter(prefix="/receipts")


def _enforce_rate_limit(request: Request, limiter) -> None:
    identity = request.client.host if request.client else "unknown"
    decision = limiter.check(identity)
    if not decision.allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )


def _parse_verification_id(verification_id: str) -> None:
    try:
        uuid.UUID(verification_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="verification_id must be a UUID") from exc


@router.get("/{verification_id}")
def get_receipt(verification_id: str, request: Request) -> dict:
    _enforce_rate_limit(request, receipt_read_limiter)
    _parse_verification_id(verification_id)

    artifact = store.get(verification_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Verification receipt not found")

    return {
        "receipt": artifact.model_dump(mode="json"),
        "receipt_digest": artifact_digest(artifact),
        "attested": artifact.signature is not None,
    }


@router.get("/{verification_id}/verify")
def verify_receipt(verification_id: str, request: Request) -> dict:
    _enforce_rate_limit(request, receipt_verify_limiter)
    _parse_verification_id(verification_id)

    artifact = store.get(verification_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Verification receipt not found")

    if not artifact.signature or not artifact.signature_algorithm:
        return {
            "verification_id": verification_id,
            "valid": False,
            "reason": "Receipt is not signed",
        }

    if not verify_artifact_signature(artifact):
        return {
            "verification_id": verification_id,
            "valid": False,
            "reason": "Signature verification failed or signing key is unavailable",
        }

    algorithm, key_id = artifact.signature_algorithm.split(":", 1)
    return {
        "verification_id": verification_id,
        "valid": True,
        "algorithm": algorithm,
        "key_id": key_id,
        "receipt_digest": artifact_digest(artifact),
    }
