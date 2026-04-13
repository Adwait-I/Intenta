"""
INTENTA — MongoDB Client
Async Motor client with connection pooling and health check.
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger("mongo")
settings = get_settings()

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo() -> None:
    global _client, _db
    try:
        _client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1,
        )
        _db = _client[settings.mongodb_db_name]
        # Verify connection
        await _client.admin.command("ping")
        logger.info("mongodb_connected", db=settings.mongodb_db_name)
    except Exception as e:
        logger.warning("mongodb_connection_failed", error=str(e), hint="MongoDB may not be running")
        _client = None
        _db = None


async def close_mongo_connection() -> None:
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("mongodb_disconnected")


def get_database() -> Optional[AsyncIOMotorDatabase]:
    return _db


def get_client() -> Optional[AsyncIOMotorClient]:
    return _client
