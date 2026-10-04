from __future__ import annotations

from .contracts import (
    Evidence,
    ProfessionalEvidenceItem,
    ProfessionalEvidenceStatus,
    VerificationResponse,
)


def _location(item: Evidence) -> str | None:
    if not isinstance(item.details, dict):
        return None
    location = item.details.get("location")
    if isinstance(location, str) and location.strip():
        return location.strip()

    frame = item.details.get("frame_index")
    timestamp = item.details.get("timestamp_ms")
    if isinstance(frame, int) and isinstance(timestamp, (int, float)):
        return f"frame={frame};timestamp_ms={timestamp}"
    if isinstance(frame, int):
        return f"frame={frame}"
    if isinstance(timestamp, (int, float)):
        return f"timestamp_ms={timestamp}"
    return None


def _cctv_limitations(item: Evidence) -> list[str]:
    if not isinstance(item.details, dict):
        return []
    if not item.signal.startswith(("cctv.", "face.")):
        return []
    limitations = item.details.get("limitations", [])
    if not isinstance(limitations, list):
        return []
    return [value for value in limitations if isinstance(value, str) and value.strip()]


def enrich_professional_evidence_item(
    item: Evidence,
    *,
    response: VerificationResponse,
    status: ProfessionalEvidenceStatus,
) -> ProfessionalEvidenceItem:
    summary = item.summary
    cctv_limits = _cctv_limitations(item)
    if cctv_limits:
        summary = f"{summary} Identity remains unverified; visibility evidence is observational only."

    return ProfessionalEvidenceItem(
        evidence_id=item.evidence_id,
        signal=item.signal,
        status=status,
        summary=summary,
        confidence=item.confidence,
        engine_version=response.engine_version,
        location=_location(item),
    )
