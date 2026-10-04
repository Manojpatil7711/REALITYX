"""Enterprise batch-document verification contracts and bounded job reference implementation.

Classification is routing only. Authenticity and authority require evidence and
must remain provider-neutral.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import hashlib
import uuid
from datetime import datetime, timezone


class DocumentKind(StrEnum):
    UNKNOWN = "unknown"
    AADHAAR = "aadhaar"
    PAN = "pan"
    PASSPORT = "passport"
    VISA = "visa"
    BANK_DOCUMENT = "bank_document"
    DRIVER_LICENSE = "driver_license"
    NATIONAL_ID = "national_id"
    RESIDENCE_PERMIT = "residence_permit"
    PHOTO = "photo"
    OTHER = "other"


class CopyStatus(StrEnum):
    UNDETERMINED = "undetermined"
    ORIGINAL_PROVENANCE_SUPPORTED = "original_provenance_supported"
    COPY_XEROX_INDICATED = "copy_xerox_indicated"


class BatchJobStatus(StrEnum):
    ACCEPTED = "accepted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True)
class BatchDocumentResult:
    document_id: str
    customer_id: str
    filename: str
    kind: DocumentKind = DocumentKind.UNKNOWN
    copy_status: CopyStatus = CopyStatus.UNDETERMINED
    verification_status: str = "uncertain"
    verification_id: str | None = None
    evidence_ids: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


@dataclass
class BatchCustomer:
    customer_id: str
    documents: list[BatchDocumentResult] = field(default_factory=list)


@dataclass
class BatchJob:
    job_id: str
    status: BatchJobStatus
    document_count: int
    created_at: datetime
    customers: dict[str, BatchCustomer] = field(default_factory=dict)


def new_batch_job(document_count: int) -> BatchJob:
    if document_count < 1:
        raise ValueError("document_count must be positive")
    return BatchJob(
        job_id=str(uuid.uuid4()),
        status=BatchJobStatus.ACCEPTED,
        document_count=document_count,
        created_at=datetime.now(timezone.utc),
    )


def document_fingerprint(filename: str, size_bytes: int) -> str:
    """Stable request-level fingerprint; never treats it as authenticity proof."""
    payload = f"{filename.strip()}:{size_bytes}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
