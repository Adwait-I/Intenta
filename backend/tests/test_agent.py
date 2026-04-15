"""
INTENTA — Unit Tests: Agent Components
Tests all 8 agent sub-modules with mocked LLM calls.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from app.schemas import IntentModel, ArchitectureModel, ComplianceModel


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def sample_intent():
    return IntentModel(
        goal="Build a payment processing platform with GDPR compliance",
        users="500,000 B2B enterprise customers",
        scale="high",
        compliance=["GDPR", "PCI_DSS"],
        integrations=["Jira", "GitHub"],
        constraints=["Must be on-prem", "99.99% uptime SLA"],
        domain="fintech",
        raw_input="Build a payment platform for 500k enterprise users with GDPR and PCI compliance",
    )


@pytest.fixture
def sample_architecture():
    return ArchitectureModel(
        pattern="event-driven-microservices",
        services=["api-gateway", "auth-service", "payment-service", "audit-service"],
        rationale="High-scale fintech requires event-driven pattern for audit trail and resilience.",
        diagram_hint="Client → API Gateway → Services → Kafka → Consumers",
        trade_offs=["Higher complexity", "Full audit trail", "Eventually consistent"],
    )


@pytest.fixture
def sample_compliance():
    return ComplianceModel(
        applicable_regulations=["GDPR", "SOC2", "PCI_DSS"],
        rules=[],
        data_classification={"card_number": "PCI/Restricted", "email": "PII"},
        encryption_requirements=["AES-256 at rest", "TLS 1.3 in transit"],
        audit_log_events=["payment_initiated", "phi_accessed"],
    )


# ──────────────────────────────────────────────
# Intent Parser Tests
# ──────────────────────────────────────────────

class TestIntentParser:
    @pytest.mark.asyncio
    async def test_parse_valid_intent(self, sample_intent):
        mock_response = {
            "goal": sample_intent.goal,
            "users": sample_intent.users,
            "scale": "high",
            "compliance": ["GDPR", "PCI_DSS"],
            "integrations": ["Jira", "GitHub"],
            "constraints": ["Must be on-prem"],
            "domain": "fintech",
        }
        with patch("app.agent.intent_parser.llm_generate_json", new_callable=AsyncMock, return_value=mock_response):
            from app.agent.intent_parser import parse_intent
            intent = await parse_intent("Build a payment platform for enterprise users")
            assert intent.scale == "high"
            assert intent.domain == "fintech"
            assert "GDPR" in intent.compliance

    @pytest.mark.asyncio
    async def test_parse_intent_llm_failure_uses_fallback(self):
        with patch("app.agent.intent_parser.llm_generate_json", side_effect=Exception("Ollama down")):
            from app.agent.intent_parser import parse_intent
            intent = await parse_intent("Build a healthcare system for hospitals")
            assert intent.scale in {"low", "medium", "high", "enterprise"}
            assert intent.domain in {"fintech", "healthcare", "ecommerce", "saas", "government", "education", "iot", "manufacturing", "default"}

    @pytest.mark.asyncio
    async def test_parse_intent_invalid_scale_coerced(self):
        mock_response = {
            "goal": "Build system",
            "users": "users",
            "scale": "MASSIVE",  # invalid — should be coerced
            "compliance": [],
            "integrations": [],
            "constraints": [],
            "domain": "default",
        }
        with patch("app.agent.intent_parser.llm_generate_json", new_callable=AsyncMock, return_value=mock_response):
            from app.agent.intent_parser import parse_intent
            intent = await parse_intent("Build a system")
            assert intent.scale == "high"  # fallback


# ──────────────────────────────────────────────
# Architecture Generator Tests
# ──────────────────────────────────────────────

class TestArchitectureGen:
    @pytest.mark.asyncio
    async def test_fintech_gets_event_driven(self, sample_intent):
        with patch("app.agent.architecture_gen.llm_generate", new_callable=AsyncMock, return_value="Event-driven architecture selected for fintech compliance."):
            from app.agent.architecture_gen import generate_architecture
            arch = await generate_architecture(sample_intent)
            assert arch.pattern == "event-driven-microservices"
            assert len(arch.services) > 0
            assert len(arch.trade_offs) > 0

    @pytest.mark.asyncio
    async def test_low_scale_gets_monolith(self):
        from app.agent.architecture_gen import generate_architecture
        intent = IntentModel(
            goal="Internal tool", users="50 employees", scale="low",
            compliance=[], integrations=[], constraints=[],
            domain="default", raw_input="internal tool",
        )
        with patch("app.agent.architecture_gen.llm_generate", new_callable=AsyncMock, return_value="Monolith chosen for simplicity."):
            arch = await generate_architecture(intent)
            assert arch.pattern == "monolith"


# ──────────────────────────────────────────────
# Tech Stack Selector Tests
# ──────────────────────────────────────────────

class TestTechStackSelector:
    @pytest.mark.asyncio
    async def test_event_driven_includes_kafka(self, sample_intent):
        from app.agent.tech_stack_selector import select_stack
        stack = await select_stack(sample_intent, "event-driven-microservices")
        assert any("Kafka" in m for m in stack.messaging)

    @pytest.mark.asyncio
    async def test_fintech_overlay_includes_vault(self, sample_intent):
        from app.agent.tech_stack_selector import select_stack
        stack = await select_stack(sample_intent, "event-driven-microservices")
        assert any("Vault" in b for b in stack.backend)


# ──────────────────────────────────────────────
# Compliance Engine Tests
# ──────────────────────────────────────────────

class TestComplianceEngine:
    @pytest.mark.asyncio
    async def test_fintech_infers_pci(self):
        from app.agent.compliance_engine import generate_compliance
        intent = IntentModel(
            goal="Payment system", users="1M users", scale="high",
            compliance=[], integrations=[], constraints=[],
            domain="fintech", raw_input="payment system",
        )
        compliance = await generate_compliance(intent)
        assert "PCI_DSS" in compliance.applicable_regulations
        assert len(compliance.rules) > 0
        assert len(compliance.encryption_requirements) > 0

    @pytest.mark.asyncio
    async def test_healthcare_infers_hipaa(self):
        from app.agent.compliance_engine import generate_compliance
        intent = IntentModel(
            goal="Hospital management", users="clinicians", scale="medium",
            compliance=[], integrations=[], constraints=[],
            domain="healthcare", raw_input="hospital system",
        )
        compliance = await generate_compliance(intent)
        assert "HIPAA" in compliance.applicable_regulations


# ──────────────────────────────────────────────
# Governance Engine Tests
# ──────────────────────────────────────────────

class TestGovernanceEngine:
    @pytest.mark.asyncio
    async def test_governance_has_roles(self, sample_intent):
        from app.agent.governance_engine import generate_governance
        gov = await generate_governance(sample_intent)
        role_names = [r["role"] for r in gov.rbac_roles]
        assert "SuperAdmin" in role_names
        assert "Auditor" in role_names

    @pytest.mark.asyncio
    async def test_fintech_extra_roles(self, sample_intent):
        from app.agent.governance_engine import generate_governance
        gov = await generate_governance(sample_intent)
        role_names = [r["role"] for r in gov.rbac_roles]
        assert "RiskOfficer" in role_names


# ──────────────────────────────────────────────
# Metrics Tests
# ──────────────────────────────────────────────

class TestMetrics:
    def test_record_and_snapshot(self):
        from app.observability.metrics import record_request, get_metrics_snapshot
        record_request(success=True, duration_ms=150.0)
        record_request(success=False, duration_ms=3200.0)
        snapshot = get_metrics_snapshot()
        assert snapshot["counters"]["requests_total"] >= 2
        assert snapshot["counters"]["requests_success"] >= 1
        assert "request_duration_ms" in snapshot["histograms"]
