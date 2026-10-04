"""Provider verification service boundary with usage accounting.

No external credentials are accepted in request models. Concrete connectors own
provider authentication; REALITYX normalizes their response and records usage.
"""
from __future__ import annotations

from dataclasses import dataclass
from .provider_connectors import (
    ConnectorRegistry,
    ExternalVerificationStatus,
    ProviderRequest,
    normalize_response,
)
from .usage_metering import UsageEvent, UsageEventType, UsageMeter


@dataclass(frozen=True)
class ProviderVerificationOutcome:
    provider_id: str
    status: ExternalVerificationStatus
    evidence_id: str
    usage_event_id: str


class ProviderVerificationService:
    def __init__(self, registry: ConnectorRegistry, meter: UsageMeter | None = None) -> None:
        self.registry = registry
        self.meter = meter or UsageMeter()

    def verify(self, request: ProviderRequest, *, customer_id: str) -> ProviderVerificationOutcome:
        record = self.registry.get(request.provider_id)
        if record is None or not self.registry.usable(request.provider_id):
            event = UsageEvent(
                event_id=request.idempotency_key,
                customer_id=customer_id,
                verification_id=request.idempotency_key,
                event_type=UsageEventType.FAILED,
                processing_time_ms=0.0,
            )
            self.meter.record(event)
            raise ValueError("provider is not available")

        import time
        started = time.perf_counter()
        try:
            response = record.connector.verify(request)
            result = normalize_response(response)
        except Exception:
            elapsed = (time.perf_counter() - started) * 1000
            self.meter.record(UsageEvent(
                event_id=request.idempotency_key,
                customer_id=customer_id,
                verification_id=request.idempotency_key,
                event_type=UsageEventType.FAILED,
                processing_time_ms=elapsed,
                external_api_calls=1,
            ))
            raise

        elapsed = (time.perf_counter() - started) * 1000
        event_type = (
            UsageEventType.COMPLETED
            if result.status is ExternalVerificationStatus.VERIFIED
            else UsageEventType.UNCERTAIN
            if result.status is ExternalVerificationStatus.UNCERTAIN
            else UsageEventType.FAILED
            if result.status is ExternalVerificationStatus.UNAVAILABLE
            else UsageEventType.COMPLETED
        )
        self.meter.record(UsageEvent(
            event_id=request.idempotency_key,
            customer_id=customer_id,
            verification_id=request.idempotency_key,
            event_type=event_type,
            processing_time_ms=elapsed,
            external_api_calls=1,
        ))
        return ProviderVerificationOutcome(
            provider_id=result.provider_id,
            status=result.status,
            evidence_id=result.evidence.evidence_id,
            usage_event_id=request.idempotency_key,
        )
