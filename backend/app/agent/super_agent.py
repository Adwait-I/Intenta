"""
INTENTA — SuperAgent Orchestrator
Coordinates all 8 sub-agents to produce a full enterprise system design.
Runs LLM-heavy tasks concurrently using asyncio.gather() for performance.
"""
from __future__ import annotations
import asyncio
import time
import uuid
from typing import Any

from app.core.logger import get_logger
from app.schemas import GenerateResponse
from app.agent.intent_parser import parse_intent
from app.agent.architecture_gen import generate_architecture
from app.agent.tech_stack_selector import select_stack
from app.agent.code_blueprint import generate_blueprint
from app.agent.validation_engine import generate_validation
from app.agent.compliance_engine import generate_compliance
from app.agent.governance_engine import generate_governance
from app.agent.explainability import generate_explainability
from app.integrations.jira_mock import JiraMock
from app.integrations.github_mock import GitHubMock
from app.integrations.sap_mock import SAPMock
from app.integrations.servicenow_mock import ServiceNowMock
from app.db.repositories import save_session
from app.mock_smacep import RISK_ASSESSMENT, COST_ESTIMATION, DOCUMENTATION, SYSTEM_OVERVIEW, COMPLIANCE, ROADMAP, DEPLOYMENT_PLAN

logger = get_logger("super_agent")

# Integration mocks
_jira = JiraMock()
_github = GitHubMock()
_sap = SAPMock()
_servicenow = ServiceNowMock()


async def run_intenta(user_input: str, user_email: str | None = None) -> GenerateResponse:
    """
    Main SuperAgent pipeline:

    Stage 1 (sequential): Parse intent — must complete before anything else
    Stage 2 (parallel):   Architecture + Compliance (both need intent, independent of each other)
    Stage 3 (parallel):   TechStack + CodeBlueprint + Validation + Governance + Explainability
    Stage 4 (async):      Persist to MongoDB + trigger mock integrations
    """
    session_id = str(uuid.uuid4())
    start = time.monotonic()

    logger.info("superagent_start", session_id=session_id)

    # ── Stage 1: Intent Parsing ────────────────────────────────────────────
    intent = await parse_intent(user_input)
    logger.info("stage1_done", scale=intent.scale, domain=intent.domain)

    # ── Stage 2: Architecture + Compliance (parallel) ──────────────────────
    architecture, compliance = await asyncio.gather(
        generate_architecture(intent),
        generate_compliance(intent),
    )
    logger.info("stage2_done", pattern=architecture.pattern, regs=compliance.applicable_regulations)

    # ── Stage 3: Remaining agents (parallel) ──────────────────────────────
    tech_stack, code_blueprint, validation, governance, explainability = await asyncio.gather(
        select_stack(intent, architecture.pattern),
        generate_blueprint(intent, architecture, await _get_partial_stack(intent, architecture.pattern)),
        generate_validation(intent, architecture),
        generate_governance(intent),
        generate_explainability(intent, architecture, compliance),
    )
    logger.info("stage3_done", service_count=len(code_blueprint.services))

    elapsed_ms = (time.monotonic() - start) * 1000

    # ── Stage 3.5: Inject UI Demonstration Data ────────────────────────────
    if user_input and len(user_input) > 0:
        intent.goal = SYSTEM_OVERVIEW
        explainability.overall_risk_summary = RISK_ASSESSMENT
        explainability.cost_estimation = COST_ESTIMATION
        governance.documentation_plan = DOCUMENTATION
        compliance.overview_text = COMPLIANCE
        governance.development_roadmap = ROADMAP
        tech_stack.deployment_plan = DEPLOYMENT_PLAN

    # ── Stage 4: Build response ────────────────────────────────────────────
    response = GenerateResponse(
        session_id=session_id,
        user_email=user_email or "anonymous",
        intent=intent,
        architecture=architecture,
        tech_stack=tech_stack,
        code_blueprint=code_blueprint,
        validation=validation,
        compliance=compliance,
        governance=governance,
        explainability=explainability,
        processing_time_ms=round(elapsed_ms, 2),
        integrations_triggered=[],
    )

    # ── Stage 4b: Async side-effects (non-blocking) ────────────────────────
    asyncio.create_task(_run_side_effects(session_id, response, intent))

    logger.info(
        "superagent_done",
        session_id=session_id,
        duration_ms=round(elapsed_ms, 2),
    )
    return response


async def _get_partial_stack(intent, pattern):
    """Quick non-LLM stack for use within Stage 3 parallel block."""
    from app.rules.tech_rules import select_tech_stack
    from app.schemas import TechStackModel
    r = select_tech_stack(pattern=pattern, domain=intent.domain)
    return TechStackModel(
        frontend=r.frontend,
        backend=r.backend,
        database=r.database,
        messaging=r.messaging,
        infrastructure=r.infrastructure,
        rationale=r.rationale,
    )


async def _run_side_effects(
    session_id: str,
    response: GenerateResponse,
    intent,
) -> None:
    """
    Non-blocking side effects: persist to MongoDB + fire mock integrations.
    Errors here do NOT affect the API response.
    """
    triggered: list[str] = []

    # MongoDB persistence
    try:
        await save_session(session_id, response.model_dump())
        logger.info("session_saved", session_id=session_id)
    except Exception as e:
        logger.error("session_save_failed", error=str(e))

    # Mock integrations based on user-specified integrations
    integration_map = {
        "jira": (_jira, "create_project_epic"),
        "github": (_github, "create_repository"),
        "sap": (_sap, "notify_project_creation"),
        "servicenow": (_servicenow, "create_change_request"),
    }

    for integration_name in intent.integrations:
        key = integration_name.lower()
        if key in integration_map:
            mock, method = integration_map[key]
            try:
                func = getattr(mock, method)
                await func(session_id=session_id, goal=intent.goal)
                triggered.append(integration_name)
                logger.info("integration_triggered", name=integration_name)
            except Exception as e:
                logger.warning("integration_failed", name=integration_name, error=str(e))

    # Also always trigger GitHub (best practice — always create a repo)
    if "github" not in [i.lower() for i in intent.integrations]:
        try:
            await _github.create_repository(session_id=session_id, goal=intent.goal)
            triggered.append("GitHub (auto)")
        except Exception as e:
            logger.warning("github_auto_failed", error=str(e))