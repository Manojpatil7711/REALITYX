from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

from .api_keys import registry as api_key_registry
from .batch_documents import new_batch_job
from .batch_ingestion import validate_manifest
from .rate_limit import privacy_rate_limit_identity, receipt_read_limiter

router = APIRouter(prefix="/batch")
_jobs = {}


class BatchManifest(BaseModel):
    model_config = {"extra": "forbid"}
    paths: list[str] = Field(min_length=1, max_length=10_000)


def _token(authorization: str | None, x_api_key: str | None) -> str:
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:].strip()
    return (x_api_key or "").strip()


def require_batch_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    record = api_key_registry.authenticate(_token(authorization, x_api_key), "batch:verify")
    if record is None:
        raise HTTPException(status_code=401, detail="Invalid, expired, revoked, or insufficient API key")
    return record


def require_batch_read_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    record = api_key_registry.authenticate(_token(authorization, x_api_key), "batch:read")
    if record is None:
        raise HTTPException(status_code=401, detail="Invalid, expired, revoked, or insufficient API key")
    return record


def _owned(job, api_key) -> None:
    if job.owner_key_id != api_key.key_id:
        raise HTTPException(status_code=404, detail="Batch job not found")


@router.post("/jobs")
def create_batch_job(document_count: int, request: Request, _api_key=Depends(require_batch_key)) -> dict:
    if document_count < 1:
        raise HTTPException(status_code=400, detail="document_count must be positive")
    identity = privacy_rate_limit_identity("batch-create", _api_key.key_id, request.client.host if request.client else None)
    decision = receipt_read_limiter.check(identity)
    if not decision.allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded", headers={"Retry-After": str(decision.retry_after_seconds)})
    job = new_batch_job(document_count, owner_key_id=_api_key.key_id)
    _jobs[job.job_id] = job
    return {"job_id": job.job_id, "status": job.status.value, "document_count": job.document_count}


@router.post("/jobs/{job_id}/manifest")
def ingest_manifest(job_id: str, manifest: BatchManifest, _api_key=Depends(require_batch_key)) -> dict:
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Batch job not found")
    _owned(job, _api_key)
    try:
        files = validate_manifest(manifest.paths)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if len(files) != job.document_count:
        raise HTTPException(status_code=400, detail="Manifest document count does not match the batch job")
    return {
        "job_id": job_id,
        "status": job.status.value,
        "accepted_files": [
            {"relative_path": item.relative_path, "filename": item.filename, "extension": item.extension}
            for item in files
        ],
        "next_stage": "document_classification",
    }


@router.get("/jobs/{job_id}")
def get_batch_job(job_id: str, _api_key=Depends(require_batch_read_key)) -> dict:
    job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Batch job not found")
    _owned(job, _api_key)
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "document_count": job.document_count,
        "customers": [
            {"customer_id": c.customer_id, "documents": [d.__dict__ for d in c.documents]}
            for c in job.customers.values()
        ],
    }
