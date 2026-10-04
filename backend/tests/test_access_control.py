from app.access_control import (
    AccessRole,
    Permission,
    can_access,
    is_owner_only,
    permissions_for,
)


def test_master_control_is_owner_only():
    assert is_owner_only(Permission.MASTER_CONTROL)
    assert can_access(AccessRole.OWNER, Permission.MASTER_CONTROL)
    for role in AccessRole:
        if role is not AccessRole.OWNER:
            assert not can_access(role, Permission.MASTER_CONTROL)


def test_operational_roles_are_scoped():
    assert can_access(AccessRole.DEVELOPER, Permission.CODE)
    assert not can_access(AccessRole.DEVELOPER, Permission.MASTER_CONTROL)
    assert can_access(AccessRole.QA, Permission.TEST)
    assert not can_access(AccessRole.QA, Permission.SECURITY_TOOLS)
    assert can_access(AccessRole.FINANCE, Permission.BILLING_REPORTS)
    assert not can_access(AccessRole.FINANCE, Permission.MASTER_CONTROL)
    assert can_access(AccessRole.PROVIDER, Permission.VERIFY)
    assert not can_access(AccessRole.PROVIDER, Permission.MASTER_CONTROL)


def test_permissions_are_immutable():
    assert isinstance(permissions_for(AccessRole.OWNER), frozenset)
