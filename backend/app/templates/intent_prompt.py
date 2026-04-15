"""
INTENTA — Prompt Templates
All LLM prompt templates for structured extraction and generation.
"""
from __future__ import annotations


INTENT_SYSTEM_PROMPT = """You are an EXPERT AI SYSTEM ARCHITECT working inside the INTENTA system.
Your goal is to generate unique, extremely detailed, and high-fidelity system designs.

🚨 CRITICAL RULES:
- BE ELABORATIVE. Avoid one-sentence responses where a paragraph would provide better technical depth.
- PROVIDE DEPTH. Discuss data flows, state management, and infrastructure boundaries in detail.
- DO NOT copy examples or previous outputs.
- ALWAYS generate fresh content based ONLY on the user input.
- Return VALID JSON ONLY. No markdown, no explanations outside the JSON."""


def intent_extraction_prompt(user_input: str) -> str:
    return f"""As an EXPERT AI SYSTEM ARCHITECT, analyze this business intent and extract structured information.
Ensure the extracted goal and context are FRESH and UNIQUE to this input.

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
    return f"""You are a senior software architect. Provide a DEEP TECHNICAL RATIONALE (3-4 detailed paragraphs)
explaining the selection of the '{pattern}' architecture pattern for this specific system.

Address:
1. Operational Efficiency: How this pattern handles the '{scale}' load.
2. Domain Alignment: Why this fits '{domain}' specific workflows.
3. Resilience & Scalability: How it handles failures and growth.
4. Security Boundaries: How it isolates sensitive data.

Context:
- Intent: {intent_summary}
- Pattern: {pattern}

Return only plain text with clear paragraph breaks. No JSON."""


def code_blueprint_prompt(
    goal: str,
    services: list[str],
    pattern: str,
    tech_stack_summary: str,
) -> str:
    services_str = "\n".join(f"- {s}" for s in services)
    return f"""You are a software architect generating an ELABORATE code blueprint.

Goal: {goal}
Architecture: {pattern}
Tech Stack: {tech_stack_summary}

For each service listed below, provide a detailed blueprint:
{services_str}

Format (JSON array):
[
  {{
    "name": "service-name",
    "responsibility": "Detailed 2-3 sentence description of internal logic and state management",
    "endpoints": [
      "POST /resource: create a resource with {{fields}}",
      "GET /resource/:id/stats: aggregate real-time metrics"
    ],
    "dependencies": ["other-service", "redis (for caching)", "postgres (main store)"]
  }}
]

Be as specific and technical as possible. Return only JSON."""


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
    return f"""As an AI lead architect, perform a CRITICAL DESIGN AUDIT.

System: {goal}
Env: {scale} scale, {regs_str} compliance.

Return a JSON object with at least 5 deep technical decisions:
{{
  "decisions": [
    {{
      "decision": "Concrete technical decision",
      "rationale": "Deep-dive into the 'why' (2-3 sentences)",
      "alternatives": ["Alternative approach A", "Alternative approach B"],
      "trade_offs": ["Pros/Cons in terms of latency, cost, or complexity"],
      "risk_level": "low/medium/high"
    }}
  ],
  "overall_risk_summary": "Extremely detailed summary of the system's risk profile (4-5 sentences)",
  "confidence_score": 0.9
}}

Return only valid JSON."""

def compliance_elaboration_prompt(goal: str, regulations: list[str], rules_summary: str) -> str:
    return f"""You are a Compliance Architect. Explain exactly how these regulations apply to the current system goal.

Goal: {goal}
Regulations: {", ".join(regulations)}
Rules to Elaborate: {rules_summary}

Write a 3-paragraph executive summary on the compliance strategy. Discuss data residency, right-to-erasure, and encryption implementation specifics.
Return only plain text."""

def governance_elaboration_prompt(goal: str, roles: list[str], scale: str) -> str:
    return f"""You are a Governance Lead. Elaborate on the organizational structure designed for this system.

Goal: {goal}
Scale: {scale}
Roles: {", ".join(roles)}

Describe the operational governance model. Explain how the roles interact, the significance of the chosen MFA requirements, and the logic behind the approval workflows (SLA targets). 
Write 2-3 detailed paragraphs. Return only plain text."""
