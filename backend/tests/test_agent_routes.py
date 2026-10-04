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
