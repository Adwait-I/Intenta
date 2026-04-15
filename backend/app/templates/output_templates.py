"""
INTENTA — Output Templates
Fallback structured outputs used when LLM fails or returns unparseable responses.
"""
from __future__ import annotations


def fallback_intent(user_input: str) -> dict:
    return {
        "goal": f"Build a system based on: {user_input[:200]}",
        "users": "Enterprise users",
        "scale": "high",
        "compliance": ["GDPR", "SOC2"],
        "integrations": [],
        "constraints": [],
        "domain": "default",
    }


def fallback_architecture(pattern: str, services: list[str]) -> dict:
    return {
        "rationale": (
            f"The {pattern} pattern was selected based on scale and domain requirements. "
            "This provides the right balance of complexity and operational capability."
        )
    }


def fallback_code_blueprint(services: list[str]) -> list[dict]:
    return [
        {
            "name": svc,
            "responsibility": f"Handles {svc.replace('-', ' ')} functionality",
            "endpoints": [f"GET /{svc}", f"POST /{svc}"],
            "dependencies": ["database", "cache"],
        }
        for svc in services
    ]


def fallback_validation(services: list[str]) -> dict:
    return {
        "unit_tests": [f"Test {svc} business logic in isolation" for svc in services[:4]],
        "integration_tests": ["Test service-to-service communication", "Test DB transactions"],
        "e2e_tests": ["Full user journey: login → create → retrieve → delete"],
        "performance_benchmarks": ["p99 latency < 200ms", "10,000 RPS throughput"],
        "recommended_tools": ["pytest", "locust", "k6", "Postman/Newman"],
    }


def fallback_explainability(pattern: str, regulations: list[str]) -> dict:
    return {
        "decisions": [
            {
                "decision": f"Selected {pattern} architecture",
                "rationale": "Based on scale requirements and domain-specific needs",
                "alternatives": ["monolith", "serverless"],
                "trade_offs": ["Higher operational complexity", "Better long-term scalability"],
                "risk_level": "medium",
            },
            {
                "decision": f"Applied compliance for: {', '.join(regulations)}",
                "rationale": "Domain regulations require specific data handling controls",
                "alternatives": ["Minimal compliance baseline"],
                "trade_offs": ["Implementation overhead vs. regulatory risk"],
                "risk_level": "high" if "HIPAA" in regulations or "PCI_DSS" in regulations else "medium",
            },
        ],
        "overall_risk_summary": (
            "The system carries medium operational risk due to distributed architecture. "
            "Compliance requirements add implementation overhead but reduce legal risk. "
            "Recommended to conduct a full security review before production deployment."
        ),
        "confidence_score": 0.75,
    }
