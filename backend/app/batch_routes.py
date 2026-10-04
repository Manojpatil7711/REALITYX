from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from .api_keys import registry as api_key_registry
from .batch_documents import BatchJobStatus, new_batch_job
from .rate_limit import privacy_rate_limit_identity, receipt_read_limiter

router = APIRouter(prefix="/batch")
_jobs = {}


def require_batch_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    elif x_api_key:
        token = x_api_key.strip()
    record = api_key_registry.authenticate(token or "", "batch:verify")
    if record is None:
        raise HTTPException(status_code=401, detail="Invalid, expired, revoked, or insufficient API key")
    return record


@router.post("/jobs")
def create_batch_job(
    document_count: int,
    request: Request,
    _api_key=Depends(require_batch_key),
) -> dict:
    if document_count < 1:
        raise HTTPException(status_code=400, detail="document_count must be positive")
    identity = privacy_rate_limit_identity("batch-create", _api_key.key_id, request.client.host if request.client else None)
    decision = receipt_read_limiter.check(identity)
    if not decision.allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded", headers={"Retry-After": str(decision.retry_after_seconds)})
    job = new_batch_job(document_count)
    _jobs[job.job_id] = job
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "document_count": job.document_count,
        "next": "POST /v1/batch/jobs/{job_id}/documents",
    }


@router.get("/jobs/{job_id}")
def get_batch_job(job_id: str, _api_key=Depends(require_batch_key)) -> dict:
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Batch job not found")
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "document_count": job.document_count,
        "customers": [
            {
                "customer_id": customer.customer_id,
                "documents": [document.__dict__ for document in customer.documents],
            }
            for customer in job.customers.values()
        ],
    }
