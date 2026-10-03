"""Owner-only control plane authentication.

The master secret is intentionally never committed to source control. Set
REALITYX_OWNER_MASTER_KEY only in the production secret manager. The API compares
a keyed digest with constant-time comparison and exposes no endpoint for reading
or rotating the secret itself.
"""

from __future__ import annotations

import hashlib
import hmac
import os

from fastapi import Header, HTTPException, Request

from ..rate_limit import FixedWindowRateLimiter

_ENV_NAME = "REALITYX_OWNER_MASTER_KEY"
_OWNER_LIMITER = FixedWindowRateLimiter(limit=10, window_seconds=60)


def require_owner(
    request: Request,
    x_realityx_master_key: str | None = Header(default=None),
) -> None:
    identity = request.client.host if request.client else "unknown"
    decision = _OWNER_LIMITER.check(identity)
    if not decision.allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many owner authentication attempts; please try again later.",
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )

    configured = os.getenv(_ENV_NAME)
    if not configured:
        raise HTTPException(status_code=503, detail="Owner control plane is not configured")

    supplied = x_realityx_master_key or ""
    expected_digest = hashlib.sha256(configured.encode("utf-8")).digest()
    supplied_digest = hashlib.sha256(supplied.encode("utf-8")).digest()

    if not hmac.compare_digest(supplied_digest, expected_digest):
        raise HTTPException(status_code=403, detail="Owner access required")
