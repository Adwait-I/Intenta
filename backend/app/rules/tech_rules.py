"""
INTENTA — Rules: Tech Stack
Deterministic stack selection based on scale, domain, and architecture pattern.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TechStackRule:
    frontend: list[str]
    backend: list[str]
    database: list[str]
    messaging: list[str]
    infrastructure: list[str]
    rationale: str


# Base stacks by architecture pattern
BASE_STACKS: dict[str, TechStackRule] = {
    "monolith": TechStackRule(
        frontend=["React", "Next.js", "Tailwind CSS"],
        backend=["FastAPI (Python)", "SQLAlchemy", "Alembic"],
        database=["PostgreSQL", "Redis (cache)"],
        messaging=[],
        infrastructure=["Docker", "Nginx", "GitHub Actions CI"],
        rationale="Simple monolith: single-process Python + Postgres, fast to ship and operate.",
    ),
    "modular-monolith": TechStackRule(
        frontend=["React", "Next.js", "TypeScript"],
        backend=["FastAPI (Python)", "SQLAlchemy", "Pydantic"],
        database=["PostgreSQL", "Redis"],
        messaging=["Celery + Redis (background tasks)"],
        infrastructure=["Docker", "Nginx", "GitHub Actions CI", "Sentry"],
        rationale="Modular monolith: strong typing, background tasks via Celery, easy microservice extraction later.",
    ),
    "microservices": TechStackRule(
        frontend=["React Native (mobile)", "Next.js (web)", "TypeScript"],
        backend=["FastAPI per service", "gRPC (internal)", "GraphQL (API gateway)"],
        database=["PostgreSQL (transactional)", "MongoDB (documents)", "Redis (cache/session)"],
        messaging=["RabbitMQ", "Celery"],
        infrastructure=["Kubernetes", "Helm", "Istio (service mesh)", "Prometheus + Grafana", "GitHub Actions CI"],
        rationale="Microservices: independent scaling, isolated deployments, K8s orchestration.",
    ),
    "event-driven-microservices": TechStackRule(
        frontend=["React Native (mobile)", "Next.js (web)", "TypeScript"],
        backend=["FastAPI per service", "gRPC (internal)", "GraphQL (API gateway)"],
        database=["PostgreSQL", "MongoDB", "Redis", "Elasticsearch (search/analytics)"],
        messaging=["Apache Kafka", "Schema Registry (Avro)", "Dead-letter queues"],
        infrastructure=["Kubernetes", "Helm", "Istio", "Kafka (self-hosted)", "Prometheus + Grafana", "ELK Stack", "GitHub Actions CI"],
        rationale="Event-driven: full audit trail, resilient async processing, CQRS/ES-friendly.",
    ),
}

# Domain-specific overlays
DOMAIN_OVERLAYS: dict[str, dict[str, list[str]]] = {
    "fintech": {
        "backend": ["HashiCorp Vault (secrets)", "Fraud detection service"],
        "database": ["TimescaleDB (time-series transactions)"],
        "infrastructure": ["AWS KMS or self-hosted HSM"],
    },
    "healthcare": {
        "backend": ["FHIR API adapter", "HL7 parser"],
        "database": ["Encrypted PostgreSQL (pgcrypto)"],
        "infrastructure": ["HIPAA-compliant storage layer"],
    },
    "iot": {
        "backend": ["MQTT broker adapter", "Edge processing layer"],
        "database": ["InfluxDB (time-series)", "TimescaleDB"],
        "messaging": ["MQTT (edge)", "Kafka (cloud ingestion)"],
    },
}


def select_tech_stack(pattern: str, domain: str) -> TechStackRule:
    base = BASE_STACKS.get(pattern, BASE_STACKS["microservices"])
    overlay = DOMAIN_OVERLAYS.get(domain.lower(), {})

    # Merge overlays
    return TechStackRule(
        frontend=base.frontend[:],
        backend=base.backend + overlay.get("backend", []),
        database=base.database + overlay.get("database", []),
        messaging=base.messaging + overlay.get("messaging", []),
        infrastructure=base.infrastructure + overlay.get("infrastructure", []),
        rationale=base.rationale,
    )
