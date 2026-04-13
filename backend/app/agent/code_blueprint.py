"""
INTENTA — Agent: Code Blueprint Generator
LLM-powered service blueprint and folder structure generator.
"""
from __future__ import annotations
import json

from app.core.llm import llm_generate_json
from app.core.logger import get_logger
from app.schemas import IntentModel, ArchitectureModel, TechStackModel, CodeBlueprintModel, ServiceBlueprint
from app.templates.intent_prompt import code_blueprint_prompt
from app.templates.output_templates import fallback_code_blueprint

logger = get_logger("code_blueprint")

FOLDER_STRUCTURES: dict[str, dict] = {
    "monolith": {
        "src/": {
            "api/": ["routes/", "middleware/", "__init__.py"],
            "core/": ["config.py", "database.py", "security.py"],
            "models/": ["__init__.py"],
            "services/": ["__init__.py"],
            "workers/": ["__init__.py"],
        },
        "tests/": ["unit/", "integration/"],
        "Dockerfile": None,
        "docker-compose.yml": None,
    },
    "microservices": {
        "services/": {
            "api-gateway/": ["src/", "Dockerfile", "package.json"],
            "auth-service/": ["app/", "Dockerfile", "requirements.txt"],
            "core-service/": ["app/", "Dockerfile", "requirements.txt"],
            "notification-service/": ["app/", "Dockerfile", "requirements.txt"],
        },
        "infra/": {
            "k8s/": ["deployments/", "services/", "ingress/"],
            "helm/": ["charts/"],
        },
        "docker-compose.yml": None,
        ".github/workflows/": ["ci.yml", "cd.yml"],
    },
    "event-driven-microservices": {
        "services/": {
            "api-gateway/": ["src/", "Dockerfile"],
            "auth-service/": ["app/", "Dockerfile"],
            "core-service/": ["app/", "Dockerfile"],
            "audit-service/": ["app/", "Dockerfile"],
            "analytics-service/": ["app/", "Dockerfile"],
            "event-schemas/": ["avro/", "proto/"],
        },
        "infra/": {
            "k8s/": ["deployments/", "services/", "configmaps/"],
            "kafka/": ["topics.yml", "schema-registry.yml"],
            "monitoring/": ["prometheus.yml", "grafana-dashboards/"],
        },
        "docker-compose.yml": None,
        ".github/workflows/": ["ci.yml", "cd.yml"],
    },
}


async def generate_blueprint(
    intent: IntentModel,
    architecture: ArchitectureModel,
    tech_stack: TechStackModel,
) -> CodeBlueprintModel:
    logger.info("blueprint_gen_start", pattern=architecture.pattern)

    tech_summary = (
        f"Backend: {', '.join(tech_stack.backend[:3])} | "
        f"DB: {', '.join(tech_stack.database[:2])} | "
        f"Messaging: {', '.join(tech_stack.messaging[:2])}"
    )

    prompt = code_blueprint_prompt(
        goal=intent.goal,
        services=architecture.services,
        pattern=architecture.pattern,
        tech_stack_summary=tech_summary,
    )

    services: list[ServiceBlueprint] = []
    try:
        data = await llm_generate_json(prompt)
        raw_services = data if isinstance(data, list) else data.get("raw", [])
        if isinstance(raw_services, str):
            raw_services = []

        for svc_data in raw_services[:10]:  # cap at 10 services
            if isinstance(svc_data, dict):
                services.append(ServiceBlueprint(
                    name=str(svc_data.get("name", "service")),
                    responsibility=str(svc_data.get("responsibility", "")),
                    endpoints=_ensure_list(svc_data.get("endpoints", [])),
                    dependencies=_ensure_list(svc_data.get("dependencies", [])),
                ))
    except Exception as e:
        logger.warning("blueprint_llm_failed", error=str(e))

    if not services:
        logger.warning("blueprint_using_fallback")
        for fb in fallback_code_blueprint(architecture.services):
            services.append(ServiceBlueprint(**fb))

    # Determine communication style
    comm_style = "event-driven (Kafka topics)" if "event-driven" in architecture.pattern else \
                 "REST/HTTP" if "monolith" in architecture.pattern else "REST + async messaging"

    # API gateway description
    api_gateway = (
        "GraphQL API Gateway with rate limiting, JWT auth, and circuit breaker"
        if "microservices" in architecture.pattern
        else "FastAPI REST server with middleware chain"
    )

    folder_structure = FOLDER_STRUCTURES.get(
        architecture.pattern,
        FOLDER_STRUCTURES["microservices"],
    )

    blueprint = CodeBlueprintModel(
        services=services,
        folder_structure=folder_structure,
        api_gateway=api_gateway,
        communication_style=comm_style,
    )

    logger.info("blueprint_gen_done", service_count=len(services))
    return blueprint


def _ensure_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    return []
