"""Provider verification service with policy-bound evidence and metering."""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from .contracts import VerificationResult
from .provider_connectors import ConnectorRegistry, ExternalVerificationStatus, ProviderRequest, normalize_response
from .risk_assessment import RiskDomain
from .usage_metering import UsageEvent, UsageEventType, UsageMeter
from .verification_policy import AuthorityStatus, UnifiedVerificationDecision, evaluate_verification


@dataclass(frozen=True)
class ProviderVerificationOutcome:
    provider_id: str
    status: ExternalVerificationStatus
    evidence_id: str
    usage_event_id: str
    decision: UnifiedVerificationDecision


class ProviderVerificationService:
    def __init__(self, registry: ConnectorRegistry, meter: UsageMeter | None = None) -> None:
        self.registry = registry
        self.meter = meter or UsageMeter()

    def verify(
        self,
        request: ProviderRequest,
        *,
        customer_id: str,
        domain: RiskDomain = RiskDomain.UNKNOWN,
        authority_status: AuthorityStatus = AuthorityStatus.NOT_REQUIRED,
    ) -> ProviderVerificationOutcome:
        record = self.registry.get(request.provider_id)
        if record is None or not self.registry.usable(request.provider_id):
            self.meter.record(UsageEvent(
                event_id=request.idempotency_key, customer_id=customer_id,
                verification_id=request.idempotency_key,
                event_type=UsageEventType.FAILED, processing_time_ms=0.0,
            ))
            raise ValueError("provider is not available")

        started = perf_counter()
        try:
            response = record.connector.verify(request)
            result = normalize_response(response)
        except Exception:
            self.meter.record(UsageEvent(
                event_id=request.idempotency_key, customer_id=customer_id,
                verification_id=request.idempotency_key,
                event_type=UsageEventType.FAILED,
                processing_time_ms=(perf_counter() - started) * 1000,
                external_api_calls=1,
            ))
            raise

        elapsed = (perf_counter() - started) * 1000
        event_type = (
            UsageEventType.UNCERTAIN if result.status is ExternalVerificationStatus.UNCERTAIN
            else UsageEventType.FAILED if result.status is ExternalVerificationStatus.UNAVAILABLE
            else UsageEventType.COMPLETED
        )
        self.meter.record(UsageEvent(
            event_id=request.idempotency_key, customer_id=customer_id,
            verification_id=request.idempotency_key, event_type=event_type,
            processing_time_ms=elapsed, external_api_calls=1,
        ))

        fusion_result = {
            ExternalVerificationStatus.VERIFIED: VerificationResult.VERIFIED,
            ExternalVerificationStatus.NOT_VERIFIED: VerificationResult.INAUTHENTIC,
        }.get(result.status, VerificationResult.UNCERTAIN)

        decision = evaluate_verification(
            [result.evidence], domain=domain, fusion_result=fusion_result,
            fusion_confidence=result.evidence.confidence or 0.0,
            authority_status=authority_status,
        )
        return ProviderVerificationOutcome(
            provider_id=result.provider_id, status=result.status,
            evidence_id=result.evidence.evidence_id,
            usage_event_id=request.idempotency_key, decision=decision,
        )
