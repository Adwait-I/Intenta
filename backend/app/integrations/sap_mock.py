"""
INTENTA — Mock Integration: SAP
Simulates SAP project registration and cost centre allocation.
"""
from __future__ import annotations
import asyncio
import uuid
from datetime import datetime, timezone
from app.core.logger import get_logger

logger = get_logger("sap_mock")


class SAPMock:
    """Simulates SAP S/4HANA project module interactions."""

    async def notify_project_creation(self, session_id: str, goal: str) -> dict:
        await asyncio.sleep(0.05)
        project_id = f"SAP-{uuid.uuid4().hex[:8].upper()}"

        result = {
            "integration": "SAP",
            "action": "project_created",
            "sap_project_id": project_id,
            "project_name": f"INTENTA-{session_id[:8].upper()}",
            "description": goal[:200],
            "cost_centre": "CC-IT-9001",
            "budget_allocated": "TBD",
            "approver": "SAP Finance Approver (pending)",
            "wbs_element": f"WBS-{uuid.uuid4().hex[:6].upper()}",
            "status": "Draft",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("sap_project_created", sap_id=project_id)
        return result

    async def allocate_budget(self, project_id: str, amount: float, currency: str = "USD") -> dict:
        await asyncio.sleep(0.02)
        return {
            "project_id": project_id,
            "amount": amount,
            "currency": currency,
            "approval_status": "Pending Finance Review",
            "expected_approval_date": "T+3 business days",
        }
