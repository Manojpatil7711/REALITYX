from app.api_key_policy import API_KEY_POLICY


def test_api_keys_and_signing_keys_remain_separate():
    assert API_KEY_POLICY.signing_keys_are_separate is True


def test_future_security_controls_are_part_of_policy():
    assert API_KEY_POLICY.support_key_rotation
    assert API_KEY_POLICY.support_emergency_revocation
    assert API_KEY_POLICY.support_per_key_rate_limits
    assert API_KEY_POLICY.support_usage_quotas
    assert API_KEY_POLICY.support_audit_events
    assert API_KEY_POLICY.support_anomaly_detection
    assert API_KEY_POLICY.support_agent_identity
    assert API_KEY_POLICY.support_crypto_agility
