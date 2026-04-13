import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["intenta"]
    sessions = await db["intent_sessions"].find({}).to_list(10)
    print("Found sessions count:", len(sessions))
    for s in sessions:
        print("Session ID:", s.get("session_id"), "Email:", s.get("user_email"))

asyncio.run(main())
