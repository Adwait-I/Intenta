"""
INTENTA — API Tests
FastAPI endpoint tests using TestClient / httpx.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient


def _make_mock_response():
    from app.schemas import (
        GenerateResponse, IntentModel, ArchitectureModel, TechStackModel,
        CodeBlueprintModel, ValidationModel, ComplianceModel, GovernanceModel,
        ExplainabilityModel, ServiceBlueprint, ComplianceRule, DecisionEntry,
    )
    return GenerateResponse(
        session_id="test-session-001",
        intent=IntentModel(
            goal="Build test system", users="test users", scale="medium",
            compliance=["GDPR"], integrations=[], constraints=[],
            domain="saas", raw_input="test input",
        ),
        architecture=ArchitectureModel(
            pattern="microservices",
            services=["api-gateway", "core-service"],
            rationale="Test rationale",
            diagram_hint="Client → Gateway → Services",
            trade_offs=["Complexity"],
        ),
        tech_stack=TechStackModel(
            frontend=["React"], backend=["FastAPI"],
            database=["PostgreSQL"], messaging=[], infrastructure=["Docker"],
            rationale="Standard stack",
        ),
        code_blueprint=CodeBlueprintModel(
            services=[ServiceBlueprint(
                name="core-service",
                responsibility="Core business logic",
                endpoints=["GET /health", "POST /resource"],
                dependencies=["postgres"],
            )],
            folder_structure={"src/": ["api/", "models/"]},
            api_gateway="FastAPI REST",
            communication_style="REST",
        ),
        validation=ValidationModel(
            unit_tests=["Test business logic"],
            integration_tests=["Test API integration"],
            e2e_tests=["Full user flow"],
            performance_benchmarks=["p99 < 200ms"],
            recommended_tools=["pytest", "k6"],
        ),
        compliance=ComplianceModel(
            applicable_regulations=["GDPR"],
            rules=[ComplianceRule(
                regulation="GDPR",
                requirement="Data Subject Rights",
                implementation="Implement erasure endpoint",
                priority="critical",
            )],
            data_classification={"email": "PII"},
            encryption_requirements=["AES-256"],
            audit_log_events=["user_data_accessed"],
        ),
        governance=GovernanceModel(
            rbac_roles=[{"role": "Admin", "permissions": ["*"], "description": "Full access", "mfa_required": True}],
            approval_workflows=[{"name": "Deploy", "steps": ["Review", "Approve"], "sla_hours": 24, "auto_approved": False}],
            data_owners=["CTO"],
            change_management="Standard approval required",
        ),
        explainability=ExplainabilityModel(
            decisions=[DecisionEntry(
                decision="microservices chosen",
                rationale="scale requirement",
                alternatives=["monolith"],
                trade_offs=["complexity"],
                risk_level="medium",
            )],
            overall_risk_summary="Medium risk system",
            confidence_score=0.85,
        ),
        processing_time_ms=1234.5,
        integrations_triggered=[],
    )


@pytest.fixture
def client():
    with patch("app.db.mongo.connect_to_mongo", new_callable=AsyncMock), \
         patch("app.db.mongo.close_mongo_connection", new_callable=AsyncMock), \
         patch("app.core.llm.health_check", new_callable=AsyncMock, return_value=True):
        from app.main import app
        with TestClient(app) as c:
            yield c


class TestHealthEndpoints:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["app"] == "INTENTA"
        assert data["status"] == "running"

    def test_health_ok(self, client):
        with patch("app.main.health_check", new_callable=AsyncMock, return_value=True):
            r = client.get("/health")
            assert r.status_code == 200
            assert r.json()["llm_available"] is True


class TestGenerateEndpoint:
    def test_generate_success(self, client):
        mock_resp = _make_mock_response()
        with patch("app.main.run_intenta", new_callable=AsyncMock, return_value=mock_resp):
            r = client.post("/generate", json={"input": "Build a fintech platform with GDPR"})
            assert r.status_code == 200
            data = r.json()
            assert "session_id" in data
            assert "intent" in data
            assert "architecture" in data
            assert "compliance" in data
            assert "governance" in data
            assert "explainability" in data

    def test_generate_empty_input_rejected(self, client):
        r = client.post("/generate", json={"input": ""})
        assert r.status_code == 422

    def test_generate_too_short_input_rejected(self, client):
        r = client.post("/generate", json={"input": "short"})
        assert r.status_code == 422

    def test_generate_llm_unavailable_returns_503(self, client):
        with patch("app.main.run_intenta", new_callable=AsyncMock, side_effect=RuntimeError("Ollama unreachable")):
            r = client.post("/generate", json={"input": "Build a large-scale enterprise system"})
            assert r.status_code == 503
