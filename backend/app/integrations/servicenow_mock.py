"""
INTENTA — Mock Integration: ServiceNow
Simulates ServiceNow change request creation and CMDB registration.
"""
from __future__ import annotations
import asyncio
import uuid
from datetime import datetime, timezone
from app.core.logger import get_logger

logger = get_logger("servicenow_mock")


class ServiceNowMock:
    """Simulates ServiceNow ITSM API interactions."""

    async def create_change_request(self, session_id: str, goal: str) -> dict:
        await asyncio.sleep(0.05)
        cr_number = f"CHG{uuid.uuid4().int % 10000000:07d}"

        result = {
            "integration": "ServiceNow",
            "action": "create_change_request",
            "change_number": cr_number,
            "short_description": f"[INTENTA Auto-Gen] {goal[:120]}",
            "category": "Application",
            "type": "Normal",
            "risk": "Medium",
            "impact": "Medium",
            "state": "New",
            "requested_by": "intenta-system",
            "assigned_group": "IT Architecture Review Board",
            "planned_start_date": "TBD",
            "planned_end_date": "TBD",
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("servicenow_cr_created", cr_number=cr_number)
        return result

    async def register_ci(self, session_id: str, services: list[str]) -> dict:
        """Register Configuration Items in CMDB."""
        await asyncio.sleep(0.02)
        cis = [
            {
                "ci_id": f"CI-{uuid.uuid4().hex[:6].upper()}",
                "name": svc,
                "class": "Application Service",
                "relationship": "Depends on::IT Infrastructure",
            }
            for svc in services
        ]
        return {
            "cmdb_registered": len(cis),
            "cis": cis,
        }
