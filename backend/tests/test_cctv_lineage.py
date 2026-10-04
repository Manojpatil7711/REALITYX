import pytest

from app.contracts import Evidence, EvidenceKind, SignalStatus
from app.cctv_lineage import cctv_independence_group, validate_cctv_evidence_lineage


def _item(**kwargs):
    data = dict(
        evidence_id="c1",
        source_group="camera-a",
        signal="cctv.face_visibility",
        status=SignalStatus.AVAILABLE,
        kind=EvidenceKind.FACT,
        summary="face visibility",
        details={"identity_status": "UNVERIFIED", "reconstruction_allowed": False},
    )
    data.update(kwargs)
    return Evidence(**data)


def test_cctv_lineage_accepts_factual_parent():
    parent = _item(
        evidence_id="media-1",
        signal="video.integrity",
        source_group="camera-a",
    )
    child = _item(parent_evidence_ids=["media-1"])
    validate_cctv_evidence_lineage([parent, child])


def test_cctv_lineage_rejects_identity_claim():
    item = _item(details={"identity_status": "VERIFIED"})
    with pytest.raises(ValueError, match="verified identity"):
        validate_cctv_evidence_lineage([item])


def test_cctv_lineage_rejects_reconstruction_evidence():
    item = _item(details={"identity_status": "UNVERIFIED", "reconstruction_allowed": True})
    with pytest.raises(ValueError, match="reconstruction"):
        validate_cctv_evidence_lineage([item])


def test_cctv_lineage_requires_existing_parent():
    item = _item(parent_evidence_ids=["missing"])
    with pytest.raises(ValueError, match="missing parent"):
        validate_cctv_evidence_lineage([item])


def test_cctv_independence_group_is_source_group():
    item = _item(source_group="camera-b")
    assert cctv_independence_group(item) == "camera-b"
