"""
INTENTA — Agent: Explainability Engine
LLM-assisted decision justification and risk summary.
"""
from __future__ import annotations

from app.core.llm import llm_generate_json
from app.core.logger import get_logger
from app.schemas import (
    IntentModel, ArchitectureModel, ComplianceModel,
    ExplainabilityModel, DecisionEntry,
)
from app.templates.intent_prompt import explainability_prompt
from app.templates.output_templates import fallback_explainability

logger = get_logger("explainability")


async def generate_explainability(
    intent: IntentModel,
    architecture: ArchitectureModel,
    compliance: ComplianceModel,
) -> ExplainabilityModel:
    logger.info("explainability_gen_start")

    prompt = explainability_prompt(
        goal=intent.goal,
        pattern=architecture.pattern,
        regulations=compliance.applicable_regulations,
        scale=intent.scale,
    )

    try:
        data = await llm_generate_json(prompt)
        if "raw" in data or "decisions" not in data:
            raise ValueError("LLM returned unstructured response")

        decisions = [
            DecisionEntry(
                decision=str(d.get("decision", "")),
                rationale=str(d.get("rationale", "")),
                alternatives=_ensure_list(d.get("alternatives", [])),
                trade_offs=_ensure_list(d.get("trade_offs", [])),
                risk_level=str(d.get("risk_level", "medium")),
            )
            for d in data.get("decisions", [])
            if isinstance(d, dict)
        ]

        confidence = float(data.get("confidence_score", 0.8))
        confidence = max(0.0, min(1.0, confidence))

        return ExplainabilityModel(
            decisions=decisions,
            overall_risk_summary=str(data.get("overall_risk_summary", "")),
            confidence_score=confidence,
        )

    except Exception as e:
        logger.warning("explainability_llm_failed", error=str(e))
        fb = fallback_explainability(architecture.pattern, compliance.applicable_regulations)
        return ExplainabilityModel(
            decisions=[DecisionEntry(**d) for d in fb["decisions"]],
            overall_risk_summary=fb["overall_risk_summary"],
            confidence_score=fb["confidence_score"],
        )


def _ensure_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    return []
