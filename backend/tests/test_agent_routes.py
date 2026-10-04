from __future__ import annotations

import json
from datetime import datetime, timezone

from app.agent_routes import _canonical_response_digest


def test_agent_response_digest_is_deterministic():
    payload = {
        "protocol": "REALITYX-AI-AGENT-TRUST",
        "verification_id": "00000000-0000-0000-0000-000000000000",
        "result": "uncertain",
        "confidence": 0.49,
    }
    first = _canonical_response_digest(payload)
    second = _canonical_response_digest(dict(reversed(list(payload.items()))))
    assert first == second
    assert len(first) == 64


def test_agent_response_digest_changes_with_decision():
    payload = {
        "protocol": "REALITYX-AI-AGENT-TRUST",
        "verification_id": "00000000-0000-0000-0000-000000000000",
        "result": "uncertain",
        "confidence": 0.49,
    }
    changed = {**payload, "result": "verified"}
    assert _canonical_response_digest(payload) != _canonical_response_digest(changed)

def test_agent_response_digest_binds_receipt_integrity_state():
    payload = {
        "protocol": "REALITYX-AI-AGENT-TRUST",
        "verification_id": "00000000-0000-0000-0000-000000000000",
        "result": "verified",
        "confidence": 0.9,
        "receipt_digest": "a" * 64,
        "cryptographic_valid": True,
        "receipt_integrity": "valid",
        "key_id": "key-1",
        "key_status": "active",
    }
    changed = {**payload, "receipt_integrity": "invalid_signature"}
    assert _canonical_response_digest(payload) != _canonical_response_digest(changed)


def test_agent_response_digest_binds_receipt_digest():
    payload = {
        "protocol": "REALITYX-AI-AGENT-TRUST",
        "verification_id": "00000000-0000-0000-0000-000000000000",
        "receipt_digest": "a" * 64,
        "cryptographic_valid": True,
    }
    changed = {**payload, "receipt_digest": "b" * 64}
    assert _canonical_response_digest(payload) != _canonical_response_digest(changed)
