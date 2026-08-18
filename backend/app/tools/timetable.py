from typing import Any

from backend.app.services.timetable import TimetableService


class TimetableTool:
    """Timetable tools exposed to the AI orchestration layer."""

    name = "timetable"

    @staticmethod
    def execute(user_id: int) -> dict[str, Any]:
        """Get timetable for the authenticated user."""

        return TimetableService.get_timetable(user_id)