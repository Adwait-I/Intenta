"""
INTENTA — Agent: Validation Engine
LLM-assisted testing strategy generator.
"""
from __future__ import annotations

from app.core.llm import llm_generate_json
from app.core.logger import get_logger
from app.schemas import IntentModel, ArchitectureModel, ValidationModel
from app.templates.intent_prompt import validation_prompt
from app.templates.output_templates import fallback_validation

logger = get_logger("validation_engine")


async def generate_validation(intent: IntentModel, architecture: ArchitectureModel) -> ValidationModel:
    logger.info("validation_gen_start")

    prompt = validation_prompt(
        goal=intent.goal,
        pattern=architecture.pattern,
        services=architecture.services,
    )

    try:
        data = await llm_generate_json(prompt)
        if "raw" in data or not isinstance(data, dict):
            raise ValueError("LLM returned non-structured response")

        return ValidationModel(
            unit_tests=_ensure_list(data.get("unit_tests", [])),
            integration_tests=_ensure_list(data.get("integration_tests", [])),
            e2e_tests=_ensure_list(data.get("e2e_tests", [])),
            performance_benchmarks=_ensure_list(data.get("performance_benchmarks", [])),
            recommended_tools=_ensure_list(data.get("recommended_tools", [])),
        )
    except Exception as e:
        logger.warning("validation_llm_failed", error=str(e))
        fb = fallback_validation(architecture.services)
        return ValidationModel(**fb)


def _ensure_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    return []
