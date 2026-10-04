from app.provider_connectors import ConnectorRecord, ConnectorRegistry, ExternalVerificationStatus, ProviderRequest, ProviderResponse, ProviderStatus
from app.provider_service import ProviderVerificationService
from app.risk_assessment import RiskDomain
from app.usage_metering import UsageMeter
from app.verification_policy import AuthorityStatus
from app.contracts import VerificationResult


class DemoConnector:
    provider_id = "demo"
    provider_version = "1.0"

    def __init__(self, status=ExternalVerificationStatus.VERIFIED):
        self.status = status

    def verify(self, request):
        return ProviderResponse(
            provider_id="demo", provider_version="1.0", status=self.status,
            summary="authority response",
            confidence=0.97 if self.status is ExternalVerificationStatus.VERIFIED else None,
        )


def test_provider_service_normalizes_meters_and_returns_policy_decision():
    registry = ConnectorRegistry()
    registry.register(ConnectorRecord("demo", "1.0", ProviderStatus.ACTIVE, DemoConnector()))
    meter = UsageMeter()
    outcome = ProviderVerificationService(registry, meter).verify(
        ProviderRequest("demo", "subject-1", "verify", "event-1"), customer_id="customer-1"
    )
    assert outcome.status is ExternalVerificationStatus.VERIFIED
    assert outcome.decision.result is VerificationResult.VERIFIED
    assert outcome.decision.independent_source_count == 1
    assert meter.totals("customer-1")["external_api_calls"] == 1


def test_document_provider_without_authority_stays_uncertain():
    registry = ConnectorRegistry()
    registry.register(ConnectorRecord("demo", "1.0", ProviderStatus.ACTIVE, DemoConnector()))
    outcome = ProviderVerificationService(registry).verify(
        ProviderRequest("demo", "document-1", "verify", "event-2"),
        customer_id="customer-1", domain=RiskDomain.DOCUMENT,
        authority_status=AuthorityStatus.UNAVAILABLE,
    )
    assert outcome.decision.result is VerificationResult.UNCERTAIN
    assert outcome.decision.confidence <= 0.49


def test_unavailable_provider_fails_closed_and_is_metered():
    registry = ConnectorRegistry()
    registry.register(ConnectorRecord("demo", "1.0", ProviderStatus.DISABLED, DemoConnector()))
    meter = UsageMeter()
    try:
        ProviderVerificationService(registry, meter).verify(
            ProviderRequest("demo", "subject-1", "verify", "event-3"), customer_id="customer-1"
        )
    except ValueError:
        pass
    else:
        raise AssertionError("disabled provider accepted")
    assert meter.totals("customer-1")["verification_events"] == 1
