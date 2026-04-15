"""
INTENTA — Agent: Architecture Generator
Hybrid rule + LLM architecture decision engine.
"""
from __future__ import annotations

from app.core.llm import llm_generate
from app.core.logger import get_logger
from app.schemas import ArchitectureModel, IntentModel
from app.rules.architecture_rules import determine_architecture
from app.templates.intent_prompt import architecture_rationale_prompt
from app.templates.output_templates import fallback_architecture

logger = get_logger("architecture_gen")


async def generate_architecture(intent: IntentModel) -> ArchitectureModel:
    """
    Hybrid approach:
    1. Rule engine determines pattern from scale + domain (deterministic)
    2. LLM enriches with contextual rationale
    """
    logger.info("arch_gen_start", scale=intent.scale, domain=intent.domain)

    # Step 1: Rule-based decision (always deterministic)
    rule = determine_architecture(intent.scale, intent.domain)
    logger.info("arch_rule_applied", pattern=rule.pattern, services=rule.services)

    # Step 2: LLM enriches the rationale
    rationale = await _get_rationale(intent, rule.pattern)

    arch = ArchitectureModel(
        pattern=rule.pattern,
        services=rule.services,
        rationale=rationale,
        diagram_hint=rule.diagram_hint,
        trade_offs=rule.trade_offs,
    )

    logger.info("arch_gen_done", pattern=arch.pattern)
    return arch


async def _get_rationale(intent: IntentModel, pattern: str) -> str:
    prompt = architecture_rationale_prompt(
        intent_summary=intent.goal,
        pattern=pattern,
        scale=intent.scale,
        domain=intent.domain,
    )
    try:
        rationale = await llm_generate(prompt)
        if rationale and len(rationale) > 20:
            return rationale.strip()
    except Exception as e:
        logger.warning("arch_rationale_llm_failed", error=str(e))

    # Fallback
    fallback = fallback_architecture(pattern, [])
    return fallback["rationale"]
