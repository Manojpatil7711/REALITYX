from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PublicError:
    code: str
    message: str


SAFE_ERRORS = {
    "invalid_upload": PublicError(
        code="INVALID_UPLOAD",
        message="The uploaded file could not be verified safely.",
    ),
    "unsupported_format": PublicError(
        code="UNSUPPORTED_FORMAT",
        message="This file format is not supported.",
    ),
    "rate_limited": PublicError(
        code="RATE_LIMITED",
        message="Too many verification requests; please try again later.",
    ),
    "invalid_idempotency": PublicError(
        code="INVALID_IDEMPOTENCY",
        message="The verification request identifier is invalid.",
    ),
}


def public_error(name: str) -> PublicError:
    try:
        return SAFE_ERRORS[name]
    except KeyError as exc:
        raise ValueError("Unknown public error") from exc
