"""2050 capability contract.

This module is intentionally dependency-free and side-effect free.  It provides
an extensible machine-readable description of REALITYX capabilities without
activating expensive providers or changing the existing verification path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum


class CapabilityState(StrEnum):
    ACTIVE = "active"
    AVAILABLE = "available"
    GATED = "gated"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"


class CapabilityCost(StrEnum):
    FREE = "free"
    OPTIONAL = "optional"
    PAID = "paid"


@dataclass(frozen=True)
class Capability:
    id: str
    modality: str
    state: CapabilityState
    cost: CapabilityCost
    evidence_grade: bool
    version: str
    description: str


# This registry describes the contract only. It does not provision services,
# call external APIs, enable billing, or change engine execution.
CAPABILITY_REGISTRY: tuple[Capability, ...] = (
    Capability(
        "identity.sha256",
        "all",
        CapabilityState.ACTIVE,
        CapabilityCost.FREE,
        True,
        "1.0",
        "Deterministic artifact identity using SHA-256.",
    ),
    Capability(
        "ingestion.safe",
        "all",
        CapabilityState.ACTIVE,
        CapabilityCost.FREE,
        True,
        "1.0",
        "Magic-byte, parser and resource-limit validation.",
    ),
    Capability(
        "forensics.image",
        "image",
        CapabilityState.ACTIVE,
        CapabilityCost.FREE,
        True,
        "1.0",
        "Current image evidence pipeline.",
    ),
    Capability(
        "forensics.document",
        "document",
        CapabilityState.AVAILABLE,
        CapabilityCost.FREE,
        True,
        "1.0",
        "Document evidence pipeline boundary.",
    ),
    Capability(
        "forensics.video",
        "video",
        CapabilityState.GATED,
        CapabilityCost.OPTIONAL,
        True,
        "1.0",
        "Video evidence adapters can be activated without changing the result contract.",
    ),
    Capability(
        "forensics.audio",
        "audio",
        CapabilityState.GATED,
        CapabilityCost.OPTIONAL,
        True,
        "1.0",
        "Audio evidence adapters can be activated without changing the result contract.",
    ),
    Capability(
        "provenance.c2pa",
        "all",
        CapabilityState.AVAILABLE,
        CapabilityCost.FREE,
        True,
        "1.0",
        "Provenance evidence boundary; never treated as proof of truth by itself.",
    ),
    Capability(
        "attestation.receipt",
        "all",
        CapabilityState.ACTIVE,
        CapabilityCost.FREE,
        True,
        "1.0",
        "Machine-readable verification receipt boundary.",
    ),
    Capability(
        "trust.signing",
        "all",
        CapabilityState.GATED,
        CapabilityCost.OPTIONAL,
        True,
        "1.0",
        "Cryptographic signing infrastructure, disabled until operationally required.",
    ),
    Capability(
        "agent.api",
        "all",
        CapabilityState.AVAILABLE,
        CapabilityCost.FREE,
        True,
        "1.0",
        "Machine-oriented verification contract.",
    ),
)


def capability_manifest() -> list[dict[str, object]]:
    """Return a stable, JSON-serializable capability inventory."""
    return [asdict(capability) for capability in CAPABILITY_REGISTRY]
