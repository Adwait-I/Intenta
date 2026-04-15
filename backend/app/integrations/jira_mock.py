"""
INTENTA — Mock Integration: Jira
Simulates Jira project + epic creation.
"""
from __future__ import annotations
import asyncio
import uuid
from datetime import datetime, timezone
from app.core.logger import get_logger

logger = get_logger("jira_mock")


class JiraMock:
    """Simulates Jira Cloud REST API interactions."""

    BASE_URL = "https://your-org.atlassian.net"  # Mock — not called

    async def create_project_epic(self, session_id: str, goal: str) -> dict:
        await asyncio.sleep(0.05)  # Simulate network latency
        project_key = f"INTENTA-{uuid.uuid4().hex[:6].upper()}"
        epic_id = f"EPIC-{uuid.uuid4().hex[:4].upper()}"

        result = {
            "integration": "Jira",
            "action": "create_project_epic",
            "project_key": project_key,
            "epic_id": epic_id,
            "summary": f"[INTENTA] {goal[:100]}",
            "description": f"Auto-generated epic from INTENTA session {session_id}",
            "status": "To Do",
            "priority": "High",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "url": f"{self.BASE_URL}/browse/{epic_id}",
        }

        logger.info("jira_epic_created", epic_id=epic_id, project=project_key)
        return result

    async def create_sprint_stories(self, epic_id: str, services: list[str]) -> list[dict]:
        """Create one story per service."""
        await asyncio.sleep(0.05)
        stories = []
        for i, svc in enumerate(services, 1):
            story_id = f"STORY-{uuid.uuid4().hex[:4].upper()}"
            stories.append({
                "story_id": story_id,
                "epic_id": epic_id,
                "summary": f"Implement {svc}",
                "story_points": 5,
                "assignee": "unassigned",
                "sprint": "Sprint 1",
            })
        logger.info("jira_stories_created", count=len(stories))
        return stories
