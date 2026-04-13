"""
INTENTA — Agent: Governance Engine
RBAC roles and approval workflow generator.
"""
from __future__ import annotations

from app.core.logger import get_logger
from app.schemas import IntentModel, GovernanceModel

logger = get_logger("governance_engine")

# Base RBAC roles for all systems
BASE_ROLES: list[dict] = [
    {
        "role": "SuperAdmin",
        "permissions": ["*"],
        "description": "Full system access — restricted to infrastructure team",
        "mfa_required": True,
    },
    {
        "role": "SystemAdmin",
        "permissions": ["user:*", "config:*", "audit:read"],
        "description": "Manage users, config, and read audit logs",
        "mfa_required": True,
    },
    {
        "role": "Developer",
        "permissions": ["api:read", "api:write", "logs:read"],
        "description": "Development team — service-level access",
        "mfa_required": False,
    },
    {
        "role": "Analyst",
        "permissions": ["reports:read", "data:read", "dashboard:read"],
        "description": "Read-only analytical access",
        "mfa_required": False,
    },
    {
        "role": "Auditor",
        "permissions": ["audit:read", "logs:read", "reports:read"],
        "description": "Compliance audit access — read only",
        "mfa_required": True,
    },
    {
        "role": "ServiceAccount",
        "permissions": ["api:read", "api:write"],
        "description": "Machine-to-machine service tokens",
        "mfa_required": False,
    },
]

DOMAIN_EXTRA_ROLES: dict[str, list[dict]] = {
    "fintech": [
        {"role": "RiskOfficer", "permissions": ["risk:*", "compliance:read", "reports:*"], "description": "Financial risk management", "mfa_required": True},
        {"role": "ComplianceOfficer", "permissions": ["compliance:*", "audit:*", "reports:read"], "description": "Regulatory compliance oversight", "mfa_required": True},
    ],
    "healthcare": [
        {"role": "Clinician", "permissions": ["phi:read", "phi:write", "patient:*"], "description": "Medical staff patient data access", "mfa_required": True},
        {"role": "HIPAAOfficer", "permissions": ["hipaa:*", "audit:*", "phi:read"], "description": "HIPAA compliance officer", "mfa_required": True},
    ],
}

BASE_WORKFLOWS: list[dict] = [
    {
        "name": "Production Deployment",
        "steps": ["Developer → PR review", "Tech Lead approval", "QA sign-off", "Deployment to prod"],
        "sla_hours": 24,
        "auto_approved": False,
    },
    {
        "name": "Data Access Request",
        "steps": ["User → Data Owner approval", "Security review (if PII)", "Access granted with expiry"],
        "sla_hours": 48,
        "auto_approved": False,
    },
    {
        "name": "Emergency Hotfix",
        "steps": ["Developer → SystemAdmin approval", "Deploy", "Post-incident review within 24h"],
        "sla_hours": 4,
        "auto_approved": False,
    },
    {
        "name": "New User Onboarding",
        "steps": ["HR request", "SystemAdmin creates account", "MFA enrollment", "Role assignment"],
        "sla_hours": 8,
        "auto_approved": False,
    },
]


async def generate_governance(intent: IntentModel) -> GovernanceModel:
    logger.info("governance_gen_start", domain=intent.domain)

    roles = BASE_ROLES + DOMAIN_EXTRA_ROLES.get(intent.domain, [])

    # Data owners based on domain
    data_owners = _get_data_owners(intent.domain)

    # Change management level based on scale
    change_mgmt = _change_management_policy(intent.scale)

    governance = GovernanceModel(
        rbac_roles=roles,
        approval_workflows=BASE_WORKFLOWS,
        data_owners=data_owners,
        change_management=change_mgmt,
    )

    logger.info("governance_gen_done", role_count=len(roles))
    return governance


def _get_data_owners(domain: str) -> list[str]:
    base = ["CTO (system-wide)", "Engineering Lead (APIs)", "Security Officer (auth/PII)"]
    extras = {
        "fintech": ["CFO (financial data)", "Chief Risk Officer (risk models)"],
        "healthcare": ["Chief Medical Officer (PHI)", "Privacy Officer (patient data)"],
        "ecommerce": ["Head of Product (catalog)", "Head of Payments (transaction data)"],
    }
    return base + extras.get(domain, [])


def _change_management_policy(scale: str) -> str:
    policies = {
        "low": "Lightweight: PR review + self-approval for non-production. Single approver for production.",
        "medium": "Standard: PR review + 1 approver. Staging deployment required before production.",
        "high": "Strict: PR review + 2 approvers + QA sign-off + staging validation + CAB approval for major releases.",
        "enterprise": "Enterprise CAB: Formal change record, impact assessment, CAB vote, staged rollout with rollback plan. Full audit trail mandatory.",
    }
    return policies.get(scale, policies["high"])
