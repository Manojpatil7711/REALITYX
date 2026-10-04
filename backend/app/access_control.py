"""Fail-closed access policy for the REALITYX control plane.

The owner is the only principal allowed to hold Master access. Employees,
providers, and operational roles may receive scoped permissions in future,
but none can inherit Owner/Master privileges.
"""
from __future__ import annotations

from enum import StrEnum


class AccessRole(StrEnum):
    OWNER = "owner"
    DEVELOPER = "developer"
    QA = "qa"
    SUPPORT = "support"
    SECURITY = "security"
    DEVOPS = "devops"
    FINANCE = "finance"
    PROVIDER = "provider"


class Permission(StrEnum):
    MASTER_CONTROL = "master_control"
    CODE = "code"
    TEST = "test"
    SUPPORT_DATA = "support_data"
    SECURITY_TOOLS = "security_tools"
    DEPLOYMENT = "deployment"
    BILLING_REPORTS = "billing_reports"
    VERIFY = "verify"


_OWNER_ONLY = frozenset({Permission.MASTER_CONTROL})
_ROLE_PERMISSIONS: dict[AccessRole, frozenset[Permission]] = {
    AccessRole.OWNER: frozenset(Permission),
    AccessRole.DEVELOPER: frozenset({Permission.CODE, Permission.VERIFY}),
    AccessRole.QA: frozenset({Permission.TEST, Permission.VERIFY}),
    AccessRole.SUPPORT: frozenset({Permission.SUPPORT_DATA, Permission.VERIFY}),
    AccessRole.SECURITY: frozenset({Permission.SECURITY_TOOLS, Permission.VERIFY}),
    AccessRole.DEVOPS: frozenset({Permission.DEPLOYMENT, Permission.VERIFY}),
    AccessRole.FINANCE: frozenset({Permission.BILLING_REPORTS}),
    AccessRole.PROVIDER: frozenset({Permission.VERIFY}),
}


def permissions_for(role: AccessRole) -> frozenset[Permission]:
    """Return immutable least-privilege permissions for a role."""
    return _ROLE_PERMISSIONS[role]


def can_access(role: AccessRole, permission: Permission) -> bool:
    """Check a role without allowing privilege escalation."""
    return permission in permissions_for(role)


def is_owner_only(permission: Permission) -> bool:
    return permission in _OWNER_ONLY
