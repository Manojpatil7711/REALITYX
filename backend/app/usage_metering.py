"""Deterministic usage metering primitives for future REALITYX billing.

Metering records usage; it does not charge money and does not enable billing.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
import hashlib, json

METERING_VERSION="1.0"

class UsageEventType(StrEnum):
    STARTED="verification_started"
    COMPLETED="verification_completed"
    FAILED="verification_failed"
    UNCERTAIN="verification_uncertain"

@dataclass(frozen=True)
class UsageEvent:
    event_id: str
    customer_id: str
    verification_id: str
    event_type: UsageEventType
    processing_time_ms: float
    compute_units: float = 0.0
    external_api_calls: int = 0

class UsageMeter:
    def __init__(self) -> None:
        self._events: list[UsageEvent]=[]
    def record(self,event:UsageEvent)->None:
        if event.processing_time_ms < 0 or event.compute_units < 0 or event.external_api_calls < 0:
            raise ValueError("usage values cannot be negative")
        self._events.append(event)
    def events_for(self, customer_id: str) -> tuple[UsageEvent,...]:
        return tuple(e for e in self._events if e.customer_id == customer_id)
    def totals(self, customer_id: str) -> dict[str,float|int]:
        events=self.events_for(customer_id)
        return {
            "verification_events": len(events),
            "processing_time_ms": round(sum(e.processing_time_ms for e in events),3),
            "compute_units": round(sum(e.compute_units for e in events),6),
            "external_api_calls": sum(e.external_api_calls for e in events),
        }

def usage_digest(event: UsageEvent)->str:
    payload={"event_id":event.event_id,"customer_id":event.customer_id,"verification_id":event.verification_id,
             "event_type":event.event_type.value,"processing_time_ms":event.processing_time_ms,
             "compute_units":event.compute_units,"external_api_calls":event.external_api_calls}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
