from app.provider_connectors import *
from app.contracts import EvidenceKind, SignalStatus, SignalVerdict

class DemoConnector:
    provider_id="demo"
    provider_version="1.0"
    def verify(self, request): return ProviderResponse("demo","1.0",ExternalVerificationStatus.VERIFIED,"verified",reference="abc",confidence=.98)

def test_verified_response_normalizes_to_evidence():
    result=normalize_response(ProviderResponse("bank","2.1",ExternalVerificationStatus.VERIFIED,"record matched",confidence=.99))
    assert result.evidence.kind is EvidenceKind.VERDICT
    assert result.evidence.verdict is SignalVerdict.VERIFIED
    assert result.evidence.status is SignalStatus.AVAILABLE
    assert result.evidence.source_group=="provider:bank"

def test_unavailable_provider_is_not_negative_evidence():
    result=normalize_response(ProviderResponse("bank","2.1",ExternalVerificationStatus.UNAVAILABLE,"provider unavailable"))
    assert result.evidence.status is SignalStatus.UNAVAILABLE
    assert result.evidence.verdict is None

def test_invalid_confidence_fails_closed():
    try: normalize_response(ProviderResponse("bank","2.1",ExternalVerificationStatus.VERIFIED,"bad",confidence=2))
    except ValueError: pass
    else: raise AssertionError("invalid confidence accepted")

def test_registry_digest_is_deterministic():
    a=ConnectorRegistry(); b=ConnectorRegistry()
    a.register(ConnectorRecord("z","1",ProviderStatus.ACTIVE,DemoConnector()))
    a.register(ConnectorRecord("a","1",ProviderStatus.ACTIVE,DemoConnector()))
    b.register(ConnectorRecord("a","1",ProviderStatus.ACTIVE,DemoConnector()))
    b.register(ConnectorRecord("z","1",ProviderStatus.ACTIVE,DemoConnector()))
    assert a.digest()==b.digest()
