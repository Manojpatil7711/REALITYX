from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from .api_keys import registry
from .premium.owner_access import require_owner

router = APIRouter(prefix="/api-keys", dependencies=[Depends(require_owner)])


class IssueRequest(BaseModel):
    scopes: set[str] = Field(min_length=1, max_length=16)
    expires_at: datetime | None = None


@router.post("", status_code=201)
def issue_key(request: IssueRequest) -> dict:
    token, record = registry.issue(request.scopes, request.expires_at)
    return {
        "key_id": record.key_id,
        "api_key": token,
        "scopes": sorted(record.scopes),
        "created_at": record.created_at.isoformat(),
        "expires_at": record.expires_at.isoformat() if record.expires_at else None,
        "warning": "Store this API key securely; the secret is not recoverable after issuance.",
    }


@router.delete("/{key_id}")
def revoke_key(key_id: str) -> dict:
    if not registry.revoke(key_id):
        raise HTTPException(status_code=404, detail="API key not found or already revoked")
    return {"key_id": key_id, "status": "revoked"}


async def require_api_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    scope: str = "verify:image",
):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    elif x_api_key:
        token = x_api_key.strip()
    record = registry.authenticate(token or "", scope)
    if record is None:
        raise HTTPException(status_code=401, detail="Invalid, expired, revoked, or insufficient API key")
    return record
