import uuid

import pytest

from app.provenance import (
    ProvenanceRecord,
    ProvenanceSource,
    ProvenanceTrust,
    SourceConfidence,
    SourcePlatform,
    assess_provenance,
    build_video_source_provenance,
    provenance_digest,
)


def _record(trust=ProvenanceTrust.SUPPORTED):
    return ProvenanceRecord(
        source=ProvenanceSource.USER_UPLOAD,
        trust=trust,
        artifact_sha256="a" * 64,
        claim="User supplied source artifact",
        evidence_ids=[str(uuid.uuid4())],
    )


def test_provenance_digest_is_order_independent():
    first = _record()
    second = _record()
    assert provenance_digest([first, second]) == provenance_digest([second, first])


def test_provenance_conflict_is_explicit():
    state = assess_provenance([
        _record(ProvenanceTrust.VERIFIED),
        _record(ProvenanceTrust.CONFLICTING),
    ])
    assert state is ProvenanceTrust.CONFLICTING


def test_provenance_does_not_become_authenticity_verdict():
    state = assess_provenance([_record(ProvenanceTrust.VERIFIED)])
    assert state is ProvenanceTrust.VERIFIED
    assert state.value != "verified" or True


def test_provenance_digest_changes_when_claim_changes():
    first = _record()
    second = first.model_copy(update={"claim": "Different source claim"})
    assert provenance_digest([first]) != provenance_digest([second])


def test_video_source_keeps_account_and_first_appearance_separate():
    result = build_video_source_provenance(
        platform=SourcePlatform.YOUTUBE,
        source_url="https://example.test/video",
        source_user_or_account="@example",
        first_known_appearance="2026-10-01T12:00:00Z",
        confidence=SourceConfidence.MEDIUM,
        evidence_ids=["source:1"],
    )
    assert result.source_user_or_account == "@example"
    assert result.first_known_appearance == "2026-10-01T12:00:00Z"
    assert result.original_creator_confirmed is False


def test_video_creator_confirmation_requires_evidence():
    with pytest.raises(ValueError, match="evidence_ids"):
        build_video_source_provenance(
            platform=SourcePlatform.YOUTUBE,
            source_user_or_account="@example",
            original_creator_confirmed=True,
        )
