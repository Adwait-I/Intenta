"""
INTENTA — Integration Tests
End-to-end tests for the full /generate pipeline with mocked LLM responses.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


LLM_INTENT_JSON = {
    "goal": "Build a GDPR-compliant fintech payment platform for 1M users",
    "users": "1,000,000 enterprise B2B customers",
    "scale": "high",
    "compliance": ["GDPR", "PCI_DSS"],
    "integrations": ["Jira", "GitHub"],
    "constraints": ["99.99% uptime", "on-prem deployment"],
    "domain": "fintech",
}

LLM_BLUEPRINT_JSON = [
    {
        "name": "api-gateway",
        "responsibility": "Route requests and handle auth",
        "endpoints": ["GET /health", "POST /generate"],
        "dependencies": ["auth-service"],
    },
    {
        "name": "payment-service",
        "responsibility": "Process and validate payments",
        "endpoints": ["POST /payments", "GET /payments/:id", "DELETE /payments/:id"],
        "dependencies": ["api-gateway", "postgres", "kafka"],
    },
]

LLM_VALIDATION_JSON = {
    "unit_tests": ["Test payment validation logic", "Test auth token generation"],
    "integration_tests": ["Test payment service → DB", "Test Kafka event publishing"],
    "e2e_tests": ["Full payment cycle: initiate → process → confirm → audit"],
    "performance_benchmarks": ["p99 < 100ms", "10,000 TPS payment throughput"],
    "recommended_tools": ["pytest", "k6", "Postman/Newman", "Locust"],
}

LLM_EXPLAINABILITY_JSON = {
    "decisions": [
        {
            "decision": "Event-driven microservices architecture",
            "rationale": "GDPR and PCI-DSS require full audit trail; Kafka is ideal for fintech",
            "alternatives": ["microservices without Kafka", "monolith"],
            "trade_offs": ["Higher complexity", "Requires Kafka expertise"],
            "risk_level": "medium",
        }
    ],
    "overall_risk_summary": "Medium operational risk. Compliance risk low with proper controls.",
    "confidence_score": 0.92,
}


@pytest.fixture
def integration_client():
    """TestClient with DB and LLM mocked."""
    with patch("app.db.mongo.connect_to_mongo", new_callable=AsyncMock), \
         patch("app.db.mongo.close_mongo_connection", new_callable=AsyncMock), \
         patch("app.core.llm.health_check", new_callable=AsyncMock, return_value=True), \
         patch("app.db.repositories.save_session", new_callable=AsyncMock, return_value=True):
        from app.main import app
        with TestClient(app) as c:
            yield c


class TestFullPipeline:
    def test_generate_full_fintech_pipeline(self, integration_client):
        """
        End-to-end: fintech input → full structured output with all 8 sections.
        LLM calls are mocked with realistic responses.
        """
        with patch("app.agent.intent_parser.llm_generate_json", new_callable=AsyncMock, return_value=LLM_INTENT_JSON), \
             patch("app.agent.architecture_gen.llm_generate", new_callable=AsyncMock, return_value="Event-driven chosen for compliance and scale."), \
             patch("app.agent.code_blueprint.llm_generate_json", new_callable=AsyncMock, return_value=LLM_BLUEPRINT_JSON), \
             patch("app.agent.validation_engine.llm_generate_json", new_callable=AsyncMock, return_value=LLM_VALIDATION_JSON), \
             patch("app.agent.explainability.llm_generate_json", new_callable=AsyncMock, return_value=LLM_EXPLAINABILITY_JSON):

            r = integration_client.post(
                "/generate",
                json={"input": "Build a GDPR-compliant fintech payment platform for 1 million enterprise users with Jira and GitHub integration"},
            )

        assert r.status_code == 200
        data = r.json()

        # All 8 sections present
        for section in ["intent", "architecture", "tech_stack", "code_blueprint", "validation", "compliance", "governance", "explainability"]:
            assert section in data, f"Missing section: {section}"

        # Intent correctness
        assert data["intent"]["scale"] == "high"
        assert data["intent"]["domain"] == "fintech"
        assert "GDPR" in data["intent"]["compliance"]

        # Architecture correctness
        assert data["architecture"]["pattern"] == "event-driven-microservices"
        assert len(data["architecture"]["services"]) > 0

        # Tech stack includes Kafka (fintech + event-driven)
        assert any("Kafka" in m for m in data["tech_stack"]["messaging"])

        # Compliance includes PCI_DSS (inferred from fintech)
        assert "PCI_DSS" in data["compliance"]["applicable_regulations"]
        assert len(data["compliance"]["rules"]) > 0

        # Governance has roles
        role_names = [r["role"] for r in data["governance"]["rbac_roles"]]
        assert "SuperAdmin" in role_names
        assert "RiskOfficer" in role_names  # fintech extra role

        # Explainability has decisions
        assert len(data["explainability"]["decisions"]) > 0
        assert 0.0 <= data["explainability"]["confidence_score"] <= 1.0

        # Processing time recorded
        assert data["processing_time_ms"] > 0

    def test_generate_healthcare_compliance(self, integration_client):
        """Healthcare domain should include HIPAA."""
        healthcare_intent = {**LLM_INTENT_JSON, "domain": "healthcare", "compliance": ["GDPR"]}
        with patch("app.agent.intent_parser.llm_generate_json", new_callable=AsyncMock, return_value=healthcare_intent), \
             patch("app.agent.architecture_gen.llm_generate", new_callable=AsyncMock, return_value="Event-driven for healthcare."), \
             patch("app.agent.code_blueprint.llm_generate_json", new_callable=AsyncMock, return_value=LLM_BLUEPRINT_JSON), \
             patch("app.agent.validation_engine.llm_generate_json", new_callable=AsyncMock, return_value=LLM_VALIDATION_JSON), \
             patch("app.agent.explainability.llm_generate_json", new_callable=AsyncMock, return_value=LLM_EXPLAINABILITY_JSON):

            r = integration_client.post(
                "/generate",
                json={"input": "Build a hospital management system for clinicians with GDPR compliance"},
            )

        assert r.status_code == 200
        data = r.json()
        assert "HIPAA" in data["compliance"]["applicable_regulations"]
