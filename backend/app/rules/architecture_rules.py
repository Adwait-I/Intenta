"""
INTENTA — Rules: Architecture
Deterministic rules mapping scale + domain → architecture pattern.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ArchRule:
    pattern: str
    services: list[str]
    diagram_hint: str
    trade_offs: list[str]


SCALE_ARCH_MAP: dict[str, str] = {
    "low": "monolith",
    "medium": "modular-monolith",
    "high": "microservices",
    "enterprise": "event-driven-microservices",
}

DOMAIN_OVERRIDES: dict[str, str] = {
    "fintech": "event-driven-microservices",
    "healthcare": "event-driven-microservices",
    "iot": "event-driven-microservices",
    "streaming": "event-driven-microservices",
    "ecommerce": "microservices",
    "marketplace": "microservices",
}

PATTERN_SERVICES: dict[str, list[str]] = {
    "monolith": [
        "api-server", "web-ui", "worker", "scheduler",
    ],
    "modular-monolith": [
        "api-server", "auth-module", "core-module", "reporting-module",
        "worker", "scheduler",
    ],
    "microservices": [
        "api-gateway", "auth-service", "user-service", "core-service",
        "notification-service", "reporting-service", "worker-service",
    ],
    "event-driven-microservices": [
        "api-gateway", "auth-service", "user-service", "core-service",
        "event-bus", "notification-service", "audit-service",
        "analytics-service", "reporting-service",
    ],
}

TRADE_OFFS: dict[str, list[str]] = {
    "monolith": [
        "Simple to deploy and debug",
        "May become hard to scale horizontally",
        "Single point of failure risk",
    ],
    "modular-monolith": [
        "Good balance between simplicity and maintainability",
        "Easier refactor to microservices later",
        "Shared DB can become a bottleneck",
    ],
    "microservices": [
        "Independent scaling per service",
        "Higher operational complexity (K8s, service mesh)",
        "Network latency overhead between services",
    ],
    "event-driven-microservices": [
        "Excellent decoupling and resilience",
        "Full audit trail via event log",
        "Requires mature DevOps + message broker expertise",
        "Eventually-consistent data model",
    ],
}

DIAGRAM_HINTS: dict[str, str] = {
    "monolith": "Single server → DB → cache",
    "modular-monolith": "Single deploy → internal modules → shared DB",
    "microservices": "Client → API Gateway → Services → Individual DBs",
    "event-driven-microservices": "Client → API Gateway → Services → Event Bus (Kafka/RabbitMQ) → Consumers → Audit Log",
}


def determine_architecture(scale: str, domain: str) -> ArchRule:
    """Return architecture rule for given scale and domain."""
    scale_lower = scale.lower()
    domain_lower = domain.lower()

    pattern = DOMAIN_OVERRIDES.get(domain_lower) or SCALE_ARCH_MAP.get(scale_lower, "microservices")
    services = PATTERN_SERVICES.get(pattern, PATTERN_SERVICES["microservices"])
    trade_offs = TRADE_OFFS.get(pattern, [])
    diagram = DIAGRAM_HINTS.get(pattern, "")

    return ArchRule(
        pattern=pattern,
        services=services,
        diagram_hint=diagram,
        trade_offs=trade_offs,
    )
