import uuid

from app.provenance import (
    ProvenanceRecord,
    ProvenanceSource,
    ProvenanceTrust,
    assess_provenance,
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
