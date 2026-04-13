"""
INTENTA — FastAPI Application
Async entrypoint with lifespan, CORS, request logging, and MongoDB init.
"""
from __future__ import annotations
import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logger import configure_logging, get_logger
from app.core.llm import health_check, close_client
from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.db.repositories import track_user_login, list_sessions, get_session
from app.schemas import GenerateRequest, GenerateResponse, LoginTrackRequest
from app.agent.super_agent import run_intenta
from app.observability.metrics import record_request
from app.auth.router import router as auth_router
from app.auth.dependencies import get_current_user

# Bootstrap structured logging before anything else
configure_logging()
logger = get_logger("main")
settings = get_settings()


# ──────────────────────────────────────────────
# Lifespan
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", app=settings.app_name, version=settings.app_version)
    await connect_to_mongo()
    llm_ok = await health_check()
    if not llm_ok:
        logger.warning(
            "ollama_model_not_found",
            model=settings.ollama_model,
            hint="Run: docker exec ollama ollama pull mistral",
        )
    yield
    logger.info("shutdown")
    await close_mongo_connection()
    await close_client()


# ──────────────────────────────────────────────
# App factory
# ──────────────────────────────────────────────

app = FastAPI(
    title="INTENTA",
    description="AI-Native Intent-Centric Software Development System",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routers ──────────────────────────────────────────────────────────────
app.include_router(auth_router)


# ──────────────────────────────────────────────
# Request logging middleware
# ──────────────────────────────────────────────

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start = time.monotonic()
    response = await call_next(request)
    duration_ms = (time.monotonic() - start) * 1000

    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round(duration_ms, 2),
    )
    response.headers["X-Request-ID"] = request_id
    return response


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.get("/", tags=["health"])
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health", tags=["health"])
async def health():
    llm_ok = await health_check()
    return {
        "status": "healthy" if llm_ok else "degraded",
        "llm_available": llm_ok,
        "model": settings.ollama_model,
    }


@app.post("/auth/track", tags=["auth"])
async def track_login(req: LoginTrackRequest):
    """
    Called by the frontend after a successful Firebase Auth login.
    Registers the user email and increments login counts in MongoDB.
    """
    success = await track_user_login(req.email)
    if not success:
        logger.error("api_track_login_failed", email=req.email)
        raise HTTPException(status_code=500, detail="Failed to track user login")
    return {"status": "success", "email": req.email}

@app.get("/sessions", tags=["agent"])
async def get_sessions(current_user: dict = Depends(get_current_user)):
    """
    Fetch the simplified list of completed intent sessions for the authenticated user.
    """
    user_email = current_user["email"]
    sessions = await list_sessions(user_email=user_email)
    return {"status": "success", "sessions": sessions}


@app.get("/sessions/{session_id}", tags=["agent"])
async def get_single_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """
    Fetch a full session strictly verified to belong to the authenticated user.
    """
    user_email = current_user["email"]
    session = await get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.get("user_email") != user_email:
        raise HTTPException(status_code=403, detail="Not authorized to view this session")
        
    return {"status": "success", "session": session}


@app.post("/generate", response_model=GenerateResponse, tags=["agent"])
async def generate(req: GenerateRequest, current_user: dict = Depends(get_current_user)):
    """
    Main INTENTA endpoint — JWT-protected.
    User identity is pulled from the verified JWT token (not trusted from the request body).
    """
    if not req.input.strip():
        raise HTTPException(status_code=422, detail="Input cannot be empty")

    # Use the email from the verified token — ignore any client-supplied user_email
    user_email = current_user["email"]

    logger.info("generate_start", input_preview=req.input[:120], email=user_email)
    start = time.monotonic()

    try:
        result: GenerateResponse = await run_intenta(req.input, user_email)
    except RuntimeError as e:
        logger.error("generate_failed", error=str(e))
        raise HTTPException(status_code=503, detail=f"LLM unavailable: {e}")
    except Exception as e:
        logger.error("generate_error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal agent error")

    elapsed_ms = (time.monotonic() - start) * 1000
    record_request(success=True, duration_ms=elapsed_ms)
    logger.info("generate_done", session_id=result.session_id, duration_ms=round(elapsed_ms, 2))
    return result


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})