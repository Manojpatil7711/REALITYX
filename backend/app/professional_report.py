from __future__ import annotations

from .contracts import (
    Evidence,
    EvidenceStrength,
    ProfessionalEvidenceItem,
    ProfessionalVerificationReport,
    SignalStatus,
    VerificationResponse,
    VerificationResult,
)


def _strength(response: VerificationResponse) -> EvidenceStrength:
    if response.conflict:
        return EvidenceStrength.CONFLICTING
    if response.confidence >= 0.85 and response.independent_source_count >= 2:
        return EvidenceStrength.STRONG
    if response.confidence >= 0.70:
        return EvidenceStrength.MEDIUM
    if response.confidence > 0:
        return EvidenceStrength.WEAK
    return EvidenceStrength.INSUFFICIENT


def _conclusion(response: VerificationResponse) -> str:
    if response.result is VerificationResult.INAUTHENTIC:
        return "Multiple available forensic signals indicate likely manipulation or synthetic generation within the tested scope."
    if response.result is VerificationResult.VERIFIED:
        return "Available evidence met the active verification threshold, with no disqualifying contradiction detected within the tested scope."
    if response.conflict:
        return "Available evidence is materially contradictory, so REALITYX cannot safely establish authenticity."
    return "Available evidence is insufficient to establish authenticity or inauthenticity with the required confidence."


def _provenance_status(signals: list[Evidence]) -> str:
    provenance = [s for s in signals if "provenance" in s.signal.lower() or "c2pa" in s.signal.lower()]
    if not provenance:
        return "NOT_CHECKED"
    if any(s.status is SignalStatus.FAILED for s in provenance):
        return "FAILED"
    return "AVAILABLE"


def build_professional_report(response: VerificationResponse) -> ProfessionalVerificationReport:
    items = [
        ProfessionalEvidenceItem(
            evidence_id=item.evidence_id,
            signal=item.signal,
            status=item.status.value,
            summary=item.summary,
            confidence=item.confidence,
            engine_version=response.engine_version,
            location=(item.details.get("location") if isinstance(item.details, dict) else None),
        )
        for item in response.evidence
    ]
    limitations = [
        "The verdict is scoped to the artifact, active protocol, available evidence, and engine versions.",
        "A verification result is not government, legal, regulatory, or accreditation certification.",
    ]
    if response.result is VerificationResult.UNCERTAIN:
        limitations.append(
            "Evidence is insufficient to establish authenticity or inauthenticity with the required confidence."
        )
        if response.conflict:
            limitations.append("Evidence sources materially conflict and require further investigation.")
        else:
            limitations.append("Additional independent evidence may change the result.")
    if not response.independent_source_count:
        limitations.append("No independent verdict source was available.")
    return ProfessionalVerificationReport(
        verification_id=response.verification_id,
        artifact_sha256=response.sha256,
        verdict=response.result,
        conclusion=_conclusion(response),
        confidence=response.confidence,
        evidence_strength=_strength(response),
        evidence=items,
        independent_source_count=response.independent_source_count,
        conflict=response.conflict,
        provenance_status=_provenance_status(response.signals),
        protocol_version=response.protocol_version,
        engine_version=response.engine_version,
        policy_version=response.policy_version,
        evidence_graph_digest=response.evidence_graph_digest,
        limitations=limitations,
    )
