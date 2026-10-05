from app.document_identity import (
    IdentitySignals,
    group_document_identities,
)


def test_groups_aadhaar_and_pan_for_same_customer():
    docs = [
        ("aadhaar-1", IdentitySignals(name="Ravi Patil", date_of_birth="1990-01-01")),
        ("pan-1", IdentitySignals(name="Ravi Patil", date_of_birth="1990-01-01")),
        ("other", IdentitySignals(name="Sita Patil", date_of_birth="1988-02-02")),
    ]
    groups = group_document_identities(docs)
    grouped = [set(group.document_ids) for group in groups]
    assert {"aadhaar-1", "pan-1"} in grouped
    assert {"other"} in grouped


def test_conflicting_dob_does_not_merge():
    docs = [
        ("a", IdentitySignals(name="Ravi", date_of_birth="1990-01-01")),
        ("b", IdentitySignals(name="Ravi", date_of_birth="1991-01-01")),
    ]
    groups = group_document_identities(docs)
    assert all(set(group.document_ids) != {"a", "b"} for group in groups)


def test_provider_opaque_identity_evidence_can_support_grouping():
    docs = [
        ("a", IdentitySignals(opaque_identity_key="provider-token-1")),
        ("b", IdentitySignals(opaque_identity_key="provider-token-1")),
    ]
    groups = group_document_identities(docs)
    assert any(set(group.document_ids) == {"a", "b"} for group in groups)


def test_opaque_identity_evidence_is_not_exposed_as_a_reason_value():
    docs = [
        ("a", IdentitySignals(opaque_identity_key="secret-token")),
        ("b", IdentitySignals(opaque_identity_key="secret-token")),
    ]
    groups = group_document_identities(docs)
    assert len(groups) == 1
    assert "secret-token" not in repr(groups[0])
