"""
INTENTA — Auth Repository
Tries MongoDB first; falls back to in-process store when MongoDB
is unavailable (e.g. local dev without Docker).
The in-memory store is intentionally NOT persistent — it resets on
restart, which is fine for local testing.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.mongo import get_database
from app.core.logger import get_logger

logger = get_logger("auth_repo")

AUTH_USERS_COLLECTION = "auth_users"
AUTH_LOGS_COLLECTION  = "auth_logs"

# ── In-process fallback store ────────────────────────────────────────────────
# Keys = email (lowercase), values = user dict
_mem_users: dict[str, dict] = {}


def _using_mongo() -> bool:
    return get_database() is not None


# ── Internal helpers ─────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Public API ────────────────────────────────────────────────────────────────

async def find_user_by_email(email: str) -> dict | None:
    """Return the full user document or None."""
    if _using_mongo():
        db = get_database()
        try:
            doc = await db[AUTH_USERS_COLLECTION].find_one({"email": email})
            if doc:
                doc.pop("_id", None)
            return doc
        except Exception as e:
            logger.error("find_user_failed", email=email, error=str(e))
            return None
    # Fallback
    return _mem_users.get(email)


async def create_user(email: str, hashed_password: str, role: str = "user") -> bool:
    """
    Insert a new user.
    Returns False if the email already exists.
    """
    if _using_mongo():
        db = get_database()
        try:
            now = _now()
            await db[AUTH_USERS_COLLECTION].insert_one({
                "_id": email,
                "email": email,
                "hashed_password": hashed_password,
                "role": role,
                "created_at": now,
                "last_login": None,
                "login_count": 0,
                "is_active": True,
            })
            logger.info("user_created_mongo", email=email, role=role)
            return True
        except Exception as e:
            logger.warning("create_user_failed", email=email, error=str(e))
            return False
    # Fallback
    if email in _mem_users:
        logger.warning("create_user_duplicate_mem", email=email)
        return False
    _mem_users[email] = {
        "email": email,
        "hashed_password": hashed_password,
        "role": role,
        "created_at": _now(),
        "last_login": None,
        "login_count": 0,
        "is_active": True,
    }
    logger.info("user_created_mem", email=email, role=role)
    return True


async def update_last_login(email: str) -> None:
    """Stamp last_login and increment login_count on successful auth."""
    now = _now()
    if _using_mongo():
        db = get_database()
        try:
            await db[AUTH_USERS_COLLECTION].update_one(
                {"email": email},
                {"$set": {"last_login": now}, "$inc": {"login_count": 1}},
            )
            await db[AUTH_LOGS_COLLECTION].insert_one({
                "email": email, "event": "login", "timestamp": now,
            })
        except Exception as e:
            logger.error("update_last_login_failed", email=email, error=str(e))
        return
    # Fallback
    if email in _mem_users:
        _mem_users[email]["last_login"] = now
        _mem_users[email]["login_count"] = _mem_users[email].get("login_count", 0) + 1


async def deactivate_user(email: str) -> bool:
    """Soft-delete a user account."""
    if _using_mongo():
        db = get_database()
        try:
            result = await db[AUTH_USERS_COLLECTION].update_one(
                {"email": email}, {"$set": {"is_active": False}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error("deactivate_user_failed", email=email, error=str(e))
            return False
    # Fallback
    if email in _mem_users:
        _mem_users[email]["is_active"] = False
        return True
    return False


async def list_users(limit: int = 50) -> list[dict[str, Any]]:
    """Admin: list all users (hashed_password excluded)."""
    if _using_mongo():
        db = get_database()
        try:
            cursor = db[AUTH_USERS_COLLECTION].find(
                {}, {"hashed_password": 0, "_id": 0}
            ).sort("created_at", -1).limit(limit)
            return [doc async for doc in cursor]
        except Exception as e:
            logger.error("list_users_failed", error=str(e))
            return []
    # Fallback
    return [
        {k: v for k, v in u.items() if k != "hashed_password"}
        for u in list(_mem_users.values())[-limit:]
    ]
