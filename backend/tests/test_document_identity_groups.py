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
