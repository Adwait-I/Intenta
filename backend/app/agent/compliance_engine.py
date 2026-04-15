"""
INTENTA — Agent: Compliance Engine
Deterministic GDPR/SOC2/HIPAA/PCI-DSS mapping engine.
"""
from __future__ import annotations

from app.core.llm import llm_generate
from app.core.logger import get_logger
from app.schemas import IntentModel, ComplianceModel, ComplianceRule
from app.templates.intent_prompt import compliance_elaboration_prompt
from app.rules.compliance_rules import (
    get_compliance_rules,
    infer_regulations,
    get_data_classification,
)

logger = get_logger("compliance_engine")

ENCRYPTION_REQUIREMENTS_MAP: dict[str, list[str]] = {
    "GDPR": ["AES-256 encryption at rest for PII", "TLS 1.3 for data in transit"],
    "SOC2": ["AES-256 at rest", "TLS 1.3 in transit", "HSM for key management"],
    "HIPAA": ["AES-256 for PHI at rest", "TLS 1.2+ for PHI in transit", "Encryption key rotation (annual)"],
    "PCI_DSS": ["PAN tokenization (never store raw)", "TLS 1.2+ only", "Disable weak ciphers"],
}

AUDIT_LOG_EVENTS: dict[str, list[str]] = {
    "GDPR": ["user_consent_given", "user_data_accessed", "user_data_deleted", "data_export_requested"],
    "SOC2": ["admin_login", "permission_change", "data_access", "config_change", "service_restart"],
    "HIPAA": ["phi_accessed", "phi_modified", "phi_exported", "user_login_failed", "emergency_access"],
    "PCI_DSS": ["card_data_accessed", "payment_initiated", "payment_failed", "pci_scope_change"],
}


async def generate_compliance(intent: IntentModel) -> ComplianceModel:
    logger.info("compliance_gen_start", explicit_regs=intent.compliance, domain=intent.domain)

    # Infer full set of applicable regulations
    all_regs = infer_regulations(intent.domain, intent.compliance)
    logger.info("compliance_regs_inferred", regulations=all_regs)

    # Get compliance control rules
    controls = get_compliance_rules(all_regs)

    compliance_rules = [
        ComplianceRule(
            regulation=c.regulation,
            requirement=c.requirement,
            implementation=c.implementation,
            priority=c.priority,
        )
        for c in controls
    ]

    # Aggregate encryption requirements
    encryption_set: list[str] = []
    seen_enc: set[str] = set()
    for reg in all_regs:
        for req in ENCRYPTION_REQUIREMENTS_MAP.get(reg, []):
            if req not in seen_enc:
                seen_enc.add(req)
                encryption_set.append(req)

    # Aggregate audit log events
    audit_set: list[str] = []
    seen_audit: set[str] = set()
    for reg in all_regs:
        for event in AUDIT_LOG_EVENTS.get(reg, []):
            if event not in seen_audit:
                seen_audit.add(event)
                audit_set.append(event)

    # Data classification
    data_class = get_data_classification(intent.domain)

    # NEW: LLM Elaboration for extreme detail
    rules_summary = "\n".join([f"- {r.regulation}: {r.requirement}" for r in compliance_rules[:10]])
    prompt = compliance_elaboration_prompt(intent.goal, all_regs, rules_summary)
    
    try:
        overview = await llm_generate(prompt)
    except Exception as e:
        logger.warning("compliance_elaboration_failed", error=str(e))
        overview = "Automated compliance framework mapped to system requirements."

    compliance = ComplianceModel(
        applicable_regulations=all_regs,
        rules=compliance_rules,
        data_classification=data_class,
        encryption_requirements=encryption_set,
        audit_log_events=audit_set,
        overview_text=overview,
    )

    logger.info(
        "compliance_gen_done",
        regulations=all_regs,
        rule_count=len(compliance_rules),
        audit_events=len(audit_set),
    )
    return compliance
