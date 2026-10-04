from app.access_audit import AccessDecision, authorize
from app.access_control import AccessRole, Permission


def test_only_owner_can_use_master_control():
    assert authorize("owner-1", AccessRole.OWNER, Permission.MASTER_CONTROL).decision is AccessDecision.ALLOW
    assert authorize("dev-1", AccessRole.DEVELOPER, Permission.MASTER_CONTROL).decision is AccessDecision.DENY
    assert authorize("provider-1", AccessRole.PROVIDER, Permission.MASTER_CONTROL).decision is AccessDecision.DENY


def test_scoped_roles_keep_operational_permissions():
    assert authorize("dev-1", AccessRole.DEVELOPER, Permission.CODE).decision is AccessDecision.ALLOW
    assert authorize("dev-1", AccessRole.DEVELOPER, Permission.BILLING_REPORTS).decision is AccessDecision.DENY
    assert authorize("finance-1", AccessRole.FINANCE, Permission.BILLING_REPORTS).decision is AccessDecision.ALLOW


def test_audit_event_contains_no_secret_material():
    event = authorize("owner-1", AccessRole.OWNER, Permission.MASTER_CONTROL)
    assert event.actor_id == "owner-1"
    assert "secret" not in event.reason.lower()
