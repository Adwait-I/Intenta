"""
INTENTA — Agent: Tech Stack Selector
Deterministic stack selection from rule engine (no LLM needed for correctness).
"""
from __future__ import annotations

from app.core.logger import get_logger
from app.schemas import IntentModel, TechStackModel
from app.rules.tech_rules import select_tech_stack

logger = get_logger("tech_stack_selector")


async def select_stack(intent: IntentModel, architecture_pattern: str) -> TechStackModel:
    """
    Select the appropriate tech stack based on architecture pattern and domain.
    Purely deterministic — rule engine only, no LLM required.
    """
    logger.info("tech_stack_start", pattern=architecture_pattern, domain=intent.domain)

    rule = select_tech_stack(pattern=architecture_pattern, domain=intent.domain)

    stack = TechStackModel(
        frontend=rule.frontend,
        backend=rule.backend,
        database=rule.database,
        messaging=rule.messaging,
        infrastructure=rule.infrastructure,
        rationale=rule.rationale,
    )

    logger.info(
        "tech_stack_selected",
        frontend_count=len(stack.frontend),
        backend_count=len(stack.backend),
        db_count=len(stack.database),
    )
    return stack
