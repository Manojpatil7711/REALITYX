"""Deterministic capability-watch primitives for long-term reality verification.

This module does not claim to predict future AI. It records the capabilities and
versions that the verification runtime actually exposes, creates a stable
fingerprint, and makes unexpected registry changes visible to operators.
External model/benchmark providers can be connected later behind the same
contract without changing the verification decision path.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable, Type

from .engines.base import SignalEngine


@dataclass(frozen=True)
class EngineCapability:
    name: str
    version: str
    module: str


@dataclass(frozen=True)
class CapabilitySnapshot:
    protocol_version: str
    engines: tuple[EngineCapability, ...]
    fingerprint: str


def _normalise(engine_types: Iterable[Type[SignalEngine]]) -> tuple[EngineCapability, ...]:
    items = [
        EngineCapability(
            name=str(engine_type.name),
            version=str(engine_type.version),
            module=f"{engine_type.__module__}.{engine_type.__qualname__}",
        )
        for engine_type in engine_types
    ]
    return tuple(sorted(items, key=lambda item: (item.name, item.version, item.module)))


def snapshot(engine_types: Iterable[Type[SignalEngine]], protocol_version: str) -> CapabilitySnapshot:
    engines = _normalise(engine_types)
    payload = {
        "protocol_version": protocol_version,
        "engines": [item.__dict__ for item in engines],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    fingerprint = hashlib.sha256(canonical).hexdigest()
    return CapabilitySnapshot(
        protocol_version=protocol_version,
        engines=engines,
        fingerprint=fingerprint,
    )


def compare(expected: CapabilitySnapshot, current: CapabilitySnapshot) -> dict[str, object]:
    """Return an auditable drift report without changing verification policy."""
    expected_set = {(e.name, e.version, e.module) for e in expected.engines}
    current_set = {(e.name, e.version, e.module) for e in current.engines}
    return {
        "changed": expected.fingerprint != current.fingerprint,
        "protocol_changed": expected.protocol_version != current.protocol_version,
        "added": sorted(current_set - expected_set),
        "removed": sorted(expected_set - current_set),
        "expected_fingerprint": expected.fingerprint,
        "current_fingerprint": current.fingerprint,
    }
