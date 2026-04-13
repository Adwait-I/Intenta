"""
INTENTA — Agent: Intent Parser
LLM-assisted extraction of structured intent from raw user input.
"""
from __future__ import annotations

from app.core.llm import llm_generate_json
from app.core.logger import get_logger
from app.schemas import IntentModel
from app.templates.intent_prompt import INTENT_SYSTEM_PROMPT, intent_extraction_prompt
from app.templates.output_templates import fallback_intent

logger = get_logger("intent_parser")

VALID_SCALES = {"low", "medium", "high", "enterprise"}
VALID_DOMAINS = {
    "fintech", "healthcare", "ecommerce", "saas",
    "government", "education", "iot", "manufacturing", "default",
}


async def parse_intent(user_input: str) -> IntentModel:
    """
    Extract structured intent fields from raw business intent text
    using local LLM (Mistral via Ollama).
    Falls back to templates if LLM fails or returns invalid data.
    """
    logger.info("intent_parsing_start", input_len=len(user_input))

    prompt = intent_extraction_prompt(user_input)

    try:
        data = await llm_generate_json(prompt, system=INTENT_SYSTEM_PROMPT)
    except Exception as e:
        logger.warning("intent_llm_failed", error=str(e))
        data = {}

    # Use fallback if LLM returned empty or invalid
    if not data or "goal" not in data:
        logger.warning("intent_using_fallback")
        data = fallback_intent(user_input)

    # Sanitize and validate fields
    scale = data.get("scale", "high").lower()
    if scale not in VALID_SCALES:
        scale = "high"

    domain = data.get("domain", "default").lower()
    if domain not in VALID_DOMAINS:
        domain = "default"

    compliance = _ensure_list(data.get("compliance", []))
    integrations = _ensure_list(data.get("integrations", []))
    constraints = _ensure_list(data.get("constraints", []))

    intent = IntentModel(
        goal=str(data.get("goal", "Build enterprise system")),
        users=str(data.get("users", "Enterprise users")),
        scale=scale,
        compliance=compliance,
        integrations=integrations,
        constraints=constraints,
        domain=domain,
        raw_input=user_input,
    )

    logger.info(
        "intent_parsed",
        goal=intent.goal[:80],
        scale=intent.scale,
        domain=intent.domain,
        compliance=intent.compliance,
    )
    return intent


def _ensure_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        return [value] if value else []
    return []
