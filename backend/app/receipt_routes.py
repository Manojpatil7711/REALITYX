from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException

from .receipt_store import store
from .signing import artifact_digest

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
