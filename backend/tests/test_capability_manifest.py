import pytest

from app.capability_manifest import (
    CAPABILITY_REGISTRY,
    CapabilityCost,
    CapabilityState,
    capability_manifest,
)


def test_capability_ids_are_unique_and_manifest_is_stable():
    ids = [capability.id for capability in CAPABILITY_REGISTRY]
    assert len(ids) == len(set(ids))

    manifest = capability_manifest()
    assert [item["id"] for item in manifest] == ids
    assert all(set(item) == {
        "id",
        "modality",
        "state",
        "cost",
        "evidence_grade",
        "version",
        "description",
    } for item in manifest)


def test_paid_capabilities_never_start_active():
    for capability in CAPABILITY_REGISTRY:
        if capability.cost is CapabilityCost.PAID:
            assert capability.state is not CapabilityState.ACTIVE


def test_gated_capabilities_cannot_be_active_by_contract():
    gated = [c for c in CAPABILITY_REGISTRY if c.state is CapabilityState.GATED]
    assert gated
    assert all(c.state is not CapabilityState.ACTIVE for c in gated)


def test_evidence_grade_is_required_for_registered_capabilities():
    assert CAPABILITY_REGISTRY
    assert all(capability.evidence_grade for capability in CAPABILITY_REGISTRY)


def test_free_first_registry_has_no_implicit_provider_activation():
    for capability in CAPABILITY_REGISTRY:
        if capability.cost is not CapabilityCost.FREE:
            assert capability.state in {
                CapabilityState.GATED,
                CapabilityState.DISABLED,
                CapabilityState.UNAVAILABLE,
            }
