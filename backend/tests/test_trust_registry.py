from app.ai_attestation import AIProvider, ProviderTrust
from app.trust_registry import KeyStatus, TrustRecord, fingerprint_public_key, key_usable, register_key

def test_key_fingerprint_is_deterministic():
    assert fingerprint_public_key("PUBLIC-KEY") == fingerprint_public_key("PUBLIC-KEY")

def test_register_key_creates_trust_record():
    provider = AIProvider("provider-a", "2.0", ProviderTrust.REGISTERED)
    record = register_key(provider, "key-1", "PUBLIC-KEY")
    assert isinstance(record, TrustRecord)
    assert record.key.status is KeyStatus.ACTIVE
    assert key_usable(record)

def test_revoked_provider_cannot_register():
    provider = AIProvider("provider-a", "2.0", ProviderTrust.REVOKED)
    try:
        register_key(provider, "key-1", "PUBLIC-KEY")
    except ValueError:
        return
    assert False

def test_rotated_or_revoked_key_is_not_usable():
    provider = AIProvider("provider-a", "2.0", ProviderTrust.ATTESTED)
    record = register_key(provider, "key-1", "PUBLIC-KEY")
    rotated = TrustRecord(record.provider, record.key.__class__(
        record.key.provider_id, record.key.key_id,
        record.key.public_key_fingerprint, KeyStatus.ROTATED))
    revoked = TrustRecord(record.provider, record.key.__class__(
        record.key.provider_id, record.key.key_id,
        record.key.public_key_fingerprint, KeyStatus.REVOKED))
    assert not key_usable(rotated)
    assert not key_usable(revoked)
