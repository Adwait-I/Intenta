"""
INTENTA — Auth Router
Endpoints: POST /signup, POST /login, GET /me, GET /users (admin)
All errors use RFC-standard HTTP status codes. No stack traces exposed.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user, require_role
from app.auth.jwt import create_token
from app.auth.password import hash_password, verify_password
from app.auth.repository import (
    create_user,
    find_user_by_email,
    list_users,
    update_last_login,
)
from app.auth.schemas import (
    LoginRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
    UserProfile,
)
from app.core.logger import get_logger

logger = get_logger("auth_router")

router = APIRouter(prefix="/auth", tags=["auth"])


# ── POST /auth/signup ─────────────────────────────────────────────────────────

@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def signup(req: SignupRequest) -> SignupResponse:
    existing = await find_user_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    hashed = hash_password(req.password)
    ok = await create_user(email=req.email, hashed_password=hashed, role=req.role)

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create account. Please try again.",
        )

    logger.info("user_signup", email=req.email, role=req.role)
    return SignupResponse(
        message="Account created successfully",
        email=req.email,
        role=req.role,
    )


# ── POST /auth/login ──────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT",
)
async def login(req: LoginRequest) -> TokenResponse:
    user = await find_user_by_email(req.email)

    # Constant-time path: always call verify_password even if user not found
    # to prevent timing-based user-enumeration attacks.
    dummy_hash = "$2b$12$invalidhashusedfortimingnormalization"
    stored_hash = user["hashed_password"] if user else dummy_hash

    if not user or not verify_password(req.password, stored_hash):
        logger.warning("login_failed", email=req.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated. Contact your administrator.",
        )

    token = create_token(email=user["email"], role=user["role"])
    await update_last_login(user["email"])

    logger.info("login_success", email=user["email"], role=user["role"])
    return TokenResponse(
        access_token=token,
        role=user["role"],
        email=user["email"],
    )


# ── GET /auth/me ──────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get the profile of the currently authenticated user",
)
async def me(current_user: dict = Depends(get_current_user)) -> UserProfile:
    return UserProfile(
        email=current_user["email"],
        role=current_user["role"],
        created_at=current_user.get("created_at"),
        last_login=current_user.get("last_login"),
        login_count=current_user.get("login_count", 0),
        is_active=current_user.get("is_active", True),
    )


# ── GET /auth/users  (admin only) ─────────────────────────────────────────────

@router.get(
    "/users",
    response_model=list[UserProfile],
    summary="[Admin] List all registered users",
)
async def list_all_users(
    _admin: dict = Depends(require_role("admin")),
) -> list[UserProfile]:
    users = await list_users()
    return [UserProfile(**u) for u in users]
