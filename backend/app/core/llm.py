"""
INTENTA — LLM Client
Async httpx-based Ollama client with retry logic, connection pooling,
and structured error handling.
"""
import asyncio
import json
import httpx
from typing import Any, Optional

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger("llm")
settings = get_settings()

# Shared async client — created once, reused across all requests
_client: Optional[httpx.AsyncClient] = None


async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=httpx.Timeout(
                connect=10.0,
                read=settings.ollama_timeout,
                write=30.0,
                pool=5.0,
            ),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )
    return _client


async def close_client() -> None:
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


async def llm_generate(prompt: str, system: str = "") -> str:
    """
    Send a prompt to Ollama /api/generate with retry logic.
    Returns the model's text response.
    """
    client = await get_client()
    payload: dict[str, Any] = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 2048,
        },
    }
    if system:
        payload["system"] = system

    last_error: Optional[Exception] = None
    for attempt in range(1, settings.ollama_max_retries + 1):
        try:
            logger.info("llm_request", attempt=attempt, model=settings.ollama_model)
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            text: str = data.get("response", "").strip()
            logger.info("llm_response_ok", chars=len(text))
            return text

        except httpx.HTTPStatusError as e:
            last_error = e
            logger.warning("llm_http_error", status=e.response.status_code, attempt=attempt)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            last_error = e
            logger.warning("llm_connection_error", error=str(e), attempt=attempt)
        except Exception as e:
            last_error = e
            logger.error("llm_unexpected_error", error=str(e), attempt=attempt)

        if attempt < settings.ollama_max_retries:
            await asyncio.sleep(settings.ollama_retry_delay * attempt)

    raise RuntimeError(f"Ollama unreachable after {settings.ollama_max_retries} attempts: {last_error}")


async def llm_generate_json(prompt: str, system: str = "") -> dict:
    """
    Generate a response and attempt JSON parsing.
    Falls back to wrapping raw text in a dict if parsing fails.
    """
    raw = await llm_generate(prompt, system)

    # Try to extract JSON block
    if "```json" in raw:
        start = raw.find("```json") + 7
        end = raw.find("```", start)
        raw = raw[start:end].strip()
    elif "```" in raw:
        start = raw.find("```") + 3
        end = raw.find("```", start)
        raw = raw[start:end].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Return raw text under a key so callers don't crash
        return {"raw": raw}


async def health_check() -> bool:
    """Check if Ollama is reachable and the model is available."""
    try:
        client = await get_client()
        response = await client.get("/api/tags", timeout=10.0)
        response.raise_for_status()
        tags = response.json()
        models = [m["name"] for m in tags.get("models", [])]
        available = any(settings.ollama_model in m for m in models)
        logger.info("ollama_health", models=models, target_available=available)
        return available
    except Exception as e:
        logger.error("ollama_health_failed", error=str(e))
        return False