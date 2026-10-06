from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Request

from .attestation import artifact_digest, verify_artifact_signature
from .key_registry import registry
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

    if not verify_artifact_signature(artifact):
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

@router.get("/passport/{verification_id}")
def get_passport(verification_id: str, request: Request) -> dict:
    """Return the public Evidence Passport without exposing uploaded media."""
    _enforce_rate_limit(request, receipt_read_limiter)
    _parse_verification_id(verification_id)

    artifact = store.get(verification_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="Verification passport not found")

    signed = bool(artifact.signature and artifact.signature_algorithm)
    cryptographic_valid = signed and verify_artifact_signature(artifact)

    key_id = None
    key_status = "not_configured"
    algorithm = None
    if artifact.signature_algorithm and ":" in artifact.signature_algorithm:
        algorithm, key_id = artifact.signature_algorithm.split(":", 1)
        record = registry.get(key_id)
        if record and record.algorithm == algorithm:
            key_status = record.status
        else:
            key_status = "unavailable"

    return {
        "passport_version": "1.0",
        "issuer": artifact.issuer,
        "verification_id": verification_id,
        "media_sha256": artifact.media_sha256,
        "result": artifact.result.value,
        "confidence": artifact.confidence,
        "evidence_hash": artifact.evidence_hash,
        "evidence_graph_digest": artifact.evidence_graph_digest,
        "engine_version": artifact.engine_version,
        "protocol_version": artifact.protocol_version,
        "policy_version": artifact.policy_version,
        "risk_domain": artifact.risk_domain,
        "risk_level": artifact.risk_level,
        "authority_status": artifact.authority_status,
        "independent_source_count": artifact.independent_source_count,
        "conflict": artifact.conflict,
        "receipt_digest": artifact_digest(artifact),
        "attestation": {
            "signed": signed,
            "cryptographic_valid": cryptographic_valid,
            "algorithm": algorithm,
            "key_id": key_id,
            "key_status": key_status,
        },
        "limitations": [
            "The passport proves the integrity of this verification record, not the real-world truth of the underlying media.",
            "An unsigned passport is integrity-addressable but is not a cryptographic attestation.",
        ] if not cryptographic_valid else [
            "The passport proves the integrity of this verification record, not the real-world truth of the underlying media.",
        ],
    }
