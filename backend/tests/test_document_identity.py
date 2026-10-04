from app.document_identity import IdentitySignals, match_identity, pseudonymous_identity_key


def test_identity_match_requires_evidence():
    result = match_identity(
        IdentitySignals(name="Asha Patil", date_of_birth="1990-01-01"),
        IdentitySignals(name="Asha Patil", date_of_birth="1990-01-01"),
    )
    assert result.matched
    assert result.confidence == "high"


def test_conflicting_document_number_abstains():
    result = match_identity(
        IdentitySignals(name="Asha Patil", document_number="AAA111"),
        IdentitySignals(name="Asha Patil", document_number="BBB222"),
    )
    assert not result.matched
    assert result.confidence == "uncertain"


def test_pseudonymous_key_is_stable():
    signals = IdentitySignals(name="Asha Patil", date_of_birth="1990-01-01")
    assert pseudonymous_identity_key(signals) == pseudonymous_identity_key(signals)
