"""
INTENTA — Prompt Templates
All LLM prompt templates for structured extraction and generation.
"""
from __future__ import annotations


INTENT_SYSTEM_PROMPT = """You are an expert enterprise software architect working inside the INTENTA system.
Your job is to analyse a user's business intent and extract structured information.
Always respond with valid JSON only. No markdown, no explanations outside the JSON block."""


def intent_extraction_prompt(user_input: str) -> str:
    return f"""Analyse the following business intent and extract structured information.

Business Intent:
"{user_input}"

Return a JSON object with exactly these keys:
{{
  "goal": "One sentence describing the primary goal",
  "users": "Who are the end users (e.g. '10,000 enterprise employees', 'consumers globally')",
  "scale": "one of: low / medium / high / enterprise",
  "compliance": ["list of applicable regulations, e.g. GDPR, SOC2, HIPAA, PCI-DSS"],
  "integrations": ["list of external systems, e.g. Jira, SAP, Salesforce, GitHub"],
  "constraints": ["list of technical or business constraints"],
  "domain": "one of: fintech / healthcare / ecommerce / saas / government / education / iot / manufacturing / default"
}}

Scale guidance:
- low: < 1,000 users or internal tool
- medium: 1,000 – 100,000 users
- high: 100,000 – 10M users
- enterprise: > 10M users or Fortune 500 deployment

Only return valid JSON. No extra text."""


def architecture_rationale_prompt(
    intent_summary: str,
    pattern: str,
    scale: str,
    domain: str,
) -> str:
    return f"""You are a senior software architect. Given the following context, write a concise but detailed
rationale (3-5 sentences) explaining why the '{pattern}' architecture pattern was chosen.

Context:
- Intent: {intent_summary}
- Scale: {scale}
- Domain: {domain}
- Chosen Pattern: {pattern}

Return only a plain text paragraph. No JSON, no bullet points."""


def code_blueprint_prompt(
    goal: str,
    services: list[str],
    pattern: str,
    tech_stack_summary: str,
) -> str:
    services_str = "\n".join(f"- {s}" for s in services)
    return f"""You are a software architect generating a code blueprint specification.

System Goal: {goal}
Architecture Pattern: {pattern}
Services: 
{services_str}
Tech Stack: {tech_stack_summary}

For each service, return a JSON array (no wrapper object) of service blueprint objects:
[
  {{
    "name": "service-name",
    "responsibility": "What this service does",
    "endpoints": ["POST /resource", "GET /resource/:id"],
    "dependencies": ["other-service-name", "postgres"]
  }}
]

Return only valid JSON array."""


def validation_prompt(goal: str, pattern: str, services: list[str]) -> str:
    services_str = ", ".join(services)
    return f"""Generate a comprehensive testing strategy for this system.

Goal: {goal}
Pattern: {pattern}
Services: {services_str}

Return a JSON object:
{{
  "unit_tests": ["list of unit test scenarios"],
  "integration_tests": ["list of integration test scenarios"],
  "e2e_tests": ["list of end-to-end test scenarios"],
  "performance_benchmarks": ["list of performance test targets"],
  "recommended_tools": ["list of testing tools"]
}}

Return only valid JSON."""


def explainability_prompt(
    goal: str,
    pattern: str,
    regulations: list[str],
    scale: str,
) -> str:
    regs_str = ", ".join(regulations) if regulations else "none specified"
    return f"""As an AI architect, justify the top design decisions made for this system.

System Goal: {goal}
Architecture: {pattern}
Scale: {scale}
Compliance: {regs_str}

Return a JSON object:
{{
  "decisions": [
    {{
      "decision": "What was decided",
      "rationale": "Why this decision was made",
      "alternatives": ["alternative option 1", "alternative option 2"],
      "trade_offs": ["trade-off 1", "trade-off 2"],
      "risk_level": "low / medium / high"
    }}
  ],
  "overall_risk_summary": "2-3 sentence summary of overall risk profile",
  "confidence_score": 0.85
}}

Include at least 4 decisions. Return only valid JSON."""
