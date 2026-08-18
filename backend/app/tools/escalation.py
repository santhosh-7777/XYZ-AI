from typing import Any

from backend.app.services.escalation import EscalationService


class EscalationTool:
    """Escalation tool exposed to the AI orchestration layer."""

    name = "create_escalation_request"

    @staticmethod
    def create_request(
        user_id: int,
        target: str = "teacher",
    ) -> dict[str, Any]:
        return EscalationService.create_escalation_request(
            user_id=user_id,
            target=target,
        )