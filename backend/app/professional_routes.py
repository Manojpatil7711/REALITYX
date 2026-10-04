from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Request

from .professional_report import build_professional_report
from .professional_store import store
from .rate_limit import receipt_read_limiter

router = APIRouter(prefix="/professional")


@router.get("/reports/{verification_id}")
def get_professional_report(verification_id: str, request: Request) -> dict:
    decision = receipt_read_limiter.check(request.client.host if request.client else "unknown")
    if not decision.allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )
    try:
        uuid.UUID(verification_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="verification_id must be a UUID") from exc

    response = store.get(verification_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Professional verification report not found")

    report = build_professional_report(response)
    return {"report": report.model_dump(mode="json")}
