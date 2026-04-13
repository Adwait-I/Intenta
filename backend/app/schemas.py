"""
INTENTA — Pydantic v2 Schemas
Full input/output models for the /generate endpoint.
"""
from __future__ import annotations
from typing import Any, Dict, List
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Request
# ──────────────────────────────────────────────

class GenerateRequest(BaseModel):
    input: str = Field(..., min_length=10, description="Business intent description")
    user_email: str | None = Field(None, description="Email of the authenticated user")

class LoginTrackRequest(BaseModel):
    email: str = Field(..., description="User's email address")


# ──────────────────────────────────────────────
# Sub-section models
# ──────────────────────────────────────────────

class IntentModel(BaseModel):
    goal: str
    users: str
    scale: str
    compliance: List[str]
    integrations: List[str]
    constraints: List[str]
    domain: str
    raw_input: str


class ArchitectureModel(BaseModel):
    pattern: str
    services: List[str]
    rationale: str
    diagram_hint: str
    trade_offs: List[str]


class TechStackModel(BaseModel):
    frontend: List[str]
    backend: List[str]
    database: List[str]
    messaging: List[str]
    infrastructure: List[str]
    rationale: str
    deployment_plan: str = Field(default="Standard CI/CD deployment plan.")
    monitoring_observability: List[str] = Field(default=["Prometheus", "Grafana"])


class ServiceBlueprint(BaseModel):
    name: str
    responsibility: str
    endpoints: List[str]
    dependencies: List[str]


class CodeBlueprintModel(BaseModel):
    services: List[ServiceBlueprint]
    folder_structure: Dict[str, Any]
    api_gateway: str
    communication_style: str
    data_model: str = Field(default="Relational schema structured around core domain entities.")
    api_specifications: List[str] = Field(default=["RESTful standard"])


class ValidationModel(BaseModel):
    unit_tests: List[str]
    integration_tests: List[str]
    e2e_tests: List[str]
    performance_benchmarks: List[str]
    recommended_tools: List[str]


class ComplianceRule(BaseModel):
    regulation: str
    requirement: str
    implementation: str
    priority: str


class ComplianceModel(BaseModel):
    applicable_regulations: List[str]
    rules: List[ComplianceRule]
    data_classification: Dict[str, str]
    encryption_requirements: List[str]
    audit_log_events: List[str]
    security_framework: str = Field(default="Zero Trust Architecture with RBAC/ABAC.")
    overview_text: str = Field(default="")


class GovernanceModel(BaseModel):
    rbac_roles: List[Dict[str, Any]]
    approval_workflows: List[Dict[str, Any]]
    data_owners: List[str]
    change_management: str
    development_roadmap: str | List[str] = Field(default=["Phase 1: MVP", "Phase 2: Scale"])
    documentation_plan: str = Field(default="Maintain ADRs and API swagger documentation.")


class DecisionEntry(BaseModel):
    decision: str
    rationale: str
    alternatives: List[str]
    trade_offs: List[str]
    risk_level: str


class ExplainabilityModel(BaseModel):
    decisions: List[DecisionEntry]
    overall_risk_summary: str
    confidence_score: float
    cost_estimation: str = Field(default="Cloud agnostic baseline, expected moderate operational cost.")


# ──────────────────────────────────────────────
# Top-level response
# ──────────────────────────────────────────────

class GenerateResponse(BaseModel):
    session_id: str = Field(..., description="Unique ID for this INTENTA run")
    user_email: str | None = Field(None, description="Email of user who generated this")
    intent: IntentModel
    architecture: ArchitectureModel
    tech_stack: TechStackModel
    code_blueprint: CodeBlueprintModel
    validation: ValidationModel
    compliance: ComplianceModel
    governance: GovernanceModel
    explainability: ExplainabilityModel
    processing_time_ms: float
    integrations_triggered: List[str]