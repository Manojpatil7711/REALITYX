"""Central access audit boundary for privileged REALITYX operations.

This records authorization decisions without storing secrets or credentials.
Owner/Master remains the only role allowed to exercise MASTER_CONTROL.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .access_control import AccessRole, Permission, can_access


class AccessDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class AccessAuditEvent:
    actor_id: str
    role: AccessRole
    permission: Permission
    decision: AccessDecision
    reason: str


def authorize(
    actor_id: str,
    role: AccessRole,
    permission: Permission,
) -> AccessAuditEvent:
    allowed = can_access(role, permission)
    if permission is Permission.MASTER_CONTROL and role is not AccessRole.OWNER:
        allowed = False
    return AccessAuditEvent(
        actor_id=actor_id,
        role=role,
        permission=permission,
        decision=AccessDecision.ALLOW if allowed else AccessDecision.DENY,
        reason="authorized by role policy" if allowed else "least-privilege policy denied access",
    )
