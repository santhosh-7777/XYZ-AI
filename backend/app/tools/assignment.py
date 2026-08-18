from typing import Any

from backend.app.services.assignment import AssignmentService


class AssignmentTool:
    """Assignment tools exposed to the application/AI orchestration layer."""

    name = "assignments"

    @staticmethod
    def execute(user_id: int) -> dict[str, Any]:
        """Get assignment information for the authenticated user."""

        return AssignmentService.get_assignments(user_id)