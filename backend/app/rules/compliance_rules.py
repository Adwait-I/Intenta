"""
INTENTA — Rules: Compliance
Maps domains and explicit regulations to required compliance controls.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ComplianceControl:
    regulation: str
    requirement: str
    implementation: str
    priority: str  # critical / high / medium


# Full compliance rule definitions
COMPLIANCE_RULES: dict[str, list[ComplianceControl]] = {
    "GDPR": [
        ComplianceControl("GDPR", "Data Subject Rights", "Implement API endpoints for data access, rectification, erasure", "critical"),
        ComplianceControl("GDPR", "Consent Management", "Track and store explicit consent with timestamps", "critical"),
        ComplianceControl("GDPR", "Data Minimisation", "Collect only necessary personal data fields", "high"),
        ComplianceControl("GDPR", "Right to Portability", "Export user data as JSON/CSV on request", "high"),
        ComplianceControl("GDPR", "Breach Notification", "Automated alerting within 72h of data breach", "critical"),
        ComplianceControl("GDPR", "DPA Agreements", "Document all third-party data processors", "medium"),
    ],
    "SOC2": [
        ComplianceControl("SOC2", "Access Control", "MFA, least-privilege RBAC enforced at API layer", "critical"),
        ComplianceControl("SOC2", "Audit Logging", "Immutable logs for all data access and admin actions", "critical"),
        ComplianceControl("SOC2", "Encryption at Rest", "AES-256 for all stored sensitive data", "critical"),
        ComplianceControl("SOC2", "Encryption in Transit", "TLS 1.3 for all network communication", "critical"),
        ComplianceControl("SOC2", "Vulnerability Management", "Regular CVE scanning, patch within SLA", "high"),
        ComplianceControl("SOC2", "Incident Response", "Documented IR plan with RTO/RPO targets", "high"),
    ],
    "HIPAA": [
        ComplianceControl("HIPAA", "PHI Encryption", "Encrypt all Protected Health Information at rest and in transit", "critical"),
        ComplianceControl("HIPAA", "Access Controls", "Role-based access with minimum necessary standard", "critical"),
        ComplianceControl("HIPAA", "Audit Controls", "Log all PHI access with user, timestamp, action", "critical"),
        ComplianceControl("HIPAA", "Business Associate Agreements", "BAA required for all PHI-handling vendors", "high"),
        ComplianceControl("HIPAA", "Data Backup", "Regular encrypted backups with tested restore procedures", "high"),
    ],
    "PCI_DSS": [
        ComplianceControl("PCI_DSS", "Cardholder Data Protection", "Tokenize all card data; never store raw PAN", "critical"),
        ComplianceControl("PCI_DSS", "Network Segmentation", "Isolate cardholder data environment (CDE)", "critical"),
        ComplianceControl("PCI_DSS", "Penetration Testing", "Annual pen-test + quarterly ASV scans", "high"),
        ComplianceControl("PCI_DSS", "Strong Cryptography", "TLS 1.2+ only; disable SSLv3/TLS1.0", "critical"),
    ],
}

DOMAIN_COMPLIANCE_MAP: dict[str, list[str]] = {
    "fintech": ["GDPR", "SOC2", "PCI_DSS"],
    "healthcare": ["GDPR", "HIPAA", "SOC2"],
    "ecommerce": ["GDPR", "PCI_DSS"],
    "saas": ["GDPR", "SOC2"],
    "government": ["GDPR", "SOC2"],
    "education": ["GDPR"],
    "default": ["GDPR"],
}

DATA_CLASSIFICATIONS: dict[str, dict[str, str]] = {
    "fintech": {
        "account_number": "PII/Financial", "card_number": "PCI/Restricted",
        "transaction_id": "Internal", "balance": "Confidential",
        "email": "PII", "name": "PII",
    },
    "healthcare": {
        "patient_id": "PHI/Restricted", "diagnosis": "PHI/Restricted",
        "medication": "PHI/Confidential", "name": "PII",
        "email": "PII", "appointment_id": "Internal",
    },
    "default": {
        "email": "PII", "name": "PII", "ip_address": "PII",
        "user_id": "Internal", "session_token": "Restricted",
    },
}


def get_compliance_rules(regulations: list[str]) -> list[ComplianceControl]:
    rules: list[ComplianceControl] = []
    seen: set[str] = set()
    for reg in regulations:
        for rule in COMPLIANCE_RULES.get(reg.upper().replace("-", "_"), []):
            key = f"{rule.regulation}:{rule.requirement}"
            if key not in seen:
                seen.add(key)
                rules.append(rule)
    return rules


def infer_regulations(domain: str, explicit: list[str]) -> list[str]:
    domain_regs = DOMAIN_COMPLIANCE_MAP.get(domain.lower(), DOMAIN_COMPLIANCE_MAP["default"])
    combined = list(set(domain_regs + [r.upper() for r in explicit]))
    return combined


def get_data_classification(domain: str) -> dict[str, str]:
    return DATA_CLASSIFICATIONS.get(domain.lower(), DATA_CLASSIFICATIONS["default"])
