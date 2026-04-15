"""
INTENTA — MongoDB Repositories
CRUD operations for intent sessions with audit trail support.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

from app.db.mongo import get_database
from app.core.logger import get_logger

logger = get_logger("repositories")

SESSIONS_COLLECTION = "intent_sessions"
AUDIT_COLLECTION = "audit_trail"
USERS_COLLECTION = "users"
LOGIN_LOGS_COLLECTION = "login_logs"


async def save_session(session_id: str, data: dict[str, Any]) -> bool:
    """Persist a full GenerateResponse to MongoDB."""
    db = get_database()
    if db is None:
        logger.warning("save_session_skipped", reason="no_mongo_connection")
        return False

    document = {
        "_id": session_id,
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "user_email": data.get("user_email", "anonymous"),
        "data": data,
        "version": "1.0",
    }

    try:
        await db[SESSIONS_COLLECTION].insert_one(document)
        await _write_audit_log(
            session_id=session_id,
            event="session_created",
            details={"goal": data.get("intent", {}).get("goal", "")[:200]},
        )
        return True
    except Exception as e:
        logger.error("save_session_failed", session_id=session_id, error=str(e))
        return False


async def get_session(session_id: str) -> dict | None:
    """Retrieve a session by ID."""
    db = get_database()
    if db is None:
        return None

    try:
        doc = await db[SESSIONS_COLLECTION].find_one({"_id": session_id})
        if doc:
            doc.pop("_id", None)
        return doc
    except Exception as e:
        logger.error("get_session_failed", session_id=session_id, error=str(e))
        return None


async def track_user_login(email: str) -> bool:
    """Track user login: updating last_login timestamp and incrementing login count."""
    db = get_database()
    if db is None:
        logger.warning("track_login_skipped", reason="no_mongo_connection")
        return False
        
    try:
        now = datetime.now(timezone.utc).isoformat()
        
        await db[USERS_COLLECTION].update_one(
            {"email": email},
            {
                "$set": {"last_login": now},
                "$inc": {"login_count": 1},
                "$setOnInsert": {"created_at": now, "email": email}
            },
            upsert=True
        )
        
        # Explicit login trace log
        await db[LOGIN_LOGS_COLLECTION].insert_one({
            "email": email,
            "login_time": now
        })
        
        logger.info("user_login_tracked", email=email)
        return True
    except Exception as e:
        logger.error("track_login_failed", email=email, error=str(e))
        return False


async def list_sessions(user_email: str, limit: int = 20, skip: int = 0) -> list[dict]:
    """List recent sessions for a specific user (summary only)."""
    db = get_database()
    if db is None:
        return []

    try:
        cursor = db[SESSIONS_COLLECTION].find(
            {"user_email": user_email},
            {
                "session_id": 1,
                "created_at": 1,
                "data.intent.goal": 1,
                "data.intent.domain": 1,
                "data.architecture.pattern": 1,
                "data.processing_time_ms": 1,
            }
        ).sort("created_at", -1).skip(skip).limit(limit)

        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(doc)
        return results
    except Exception as e:
        logger.error("list_sessions_failed", error=str(e))
        return []


async def _write_audit_log(
    session_id: str,
    event: str,
    details: dict[str, Any],
    user: str = "system",
) -> None:
    """Write immutable audit log entry."""
    db = get_database()
    if db is None:
        return

    try:
        await db[AUDIT_COLLECTION].insert_one({
            "session_id": session_id,
            "event": event,
            "user": user,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details,
        })
    except Exception as e:
        logger.error("audit_log_failed", error=str(e))

async def delete_session(session_id: str, user_email: str) -> bool:
    """Delete a session document ensuring the user owns it."""
    db = get_database()
    if db is None:
        return False
        
    try:
        # Delete only if session_id matches and user_email matches to prevent unauthorized deletion
        result = await db[SESSIONS_COLLECTION].delete_one({
            "session_id": session_id,
            "user_email": user_email
        })
        
        if result.deleted_count > 0:
            logger.info("session_deleted", session_id=session_id)
            await _write_audit_log(session_id, "session_deleted", {"user_email": user_email}, user=user_email)
            return True
            
        return False
    except Exception as e:
        logger.error("delete_session_failed", session_id=session_id, error=str(e))
        return False
