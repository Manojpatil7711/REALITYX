from app.site_identity import (
    OwnershipStatus,
    SiteIdentity,
    identity_digest,
    load_site_identity,
)


def test_default_identity_does_not_claim_verified_ownership(monkeypatch):
    for key in (
        "REALITYX_OWNER_DISPLAY_NAME",
        "REALITYX_SITE_DOMAIN",
        "REALITYX_OWNERSHIP_STATUS",
        "REALITYX_OWNERSHIP_METHOD",
    ):
        monkeypatch.delenv(key, raising=False)

    identity = load_site_identity()

    assert identity.ownership_status is OwnershipStatus.UNVERIFIED
    assert "independently verified" in identity.verification_method


def test_configured_owner_verification_is_publicly_machine_readable(monkeypatch):
    monkeypatch.setenv("REALITYX_OWNER_DISPLAY_NAME", "REALITYX Owner")
    monkeypatch.setenv("REALITYX_SITE_DOMAIN", "example.test")
    monkeypatch.setenv("REALITYX_OWNERSHIP_STATUS", "owner_verified")
    monkeypatch.setenv("REALITYX_OWNERSHIP_METHOD", "dns-and-account-verification")

    identity = load_site_identity()
    document = identity.public_document()

    assert document["operator"] == "REALITYX Owner"
    assert document["domain"] == "example.test"
    assert document["ownership_status"] == "owner_verified"
    assert document["verification_method"] == "dns-and-account-verification"


def test_unknown_status_fails_closed():
    identity = SiteIdentity(
        product="REALITYX",
        tagline="VERIFY WHAT'S REAL.",
        operator="operator",
        domain="example.test",
        ownership_status=OwnershipStatus.UNVERIFIED,
        verification_method="not configured",
    )
    assert identity_digest(identity) == identity_digest(identity)


def test_identity_digest_changes_when_public_identity_changes():
    first = SiteIdentity(
        product="REALITYX",
        tagline="VERIFY WHAT'S REAL.",
        operator="operator",
        domain="example.test",
        ownership_status=OwnershipStatus.UNVERIFIED,
        verification_method="not configured",
    )
    second = SiteIdentity(
        product="REALITYX",
        tagline="VERIFY WHAT'S REAL.",
        operator="different operator",
        domain="example.test",
        ownership_status=OwnershipStatus.UNVERIFIED,
        verification_method="not configured",
    )
    assert identity_digest(first) != identity_digest(second)
