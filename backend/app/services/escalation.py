from typing import Any
from uuid import uuid4


class EscalationService:
    """Mock school support/escalation service."""

    @staticmethod
    def create_escalation_request(
        user_id: int,
        target: str = "teacher",
    ) -> dict[str, Any]:
        """
        Create a mock support/call request.

        This represents the external school ERP/support API.
        """

        return {
            "request_id": f"ESC-{uuid4().hex[:8].upper()}",
            "user_id": user_id,
            "target": target,
            "status": "SUBMITTED",
        }