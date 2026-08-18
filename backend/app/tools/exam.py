from typing import Any

from backend.app.services.exam import ExamService


class ExamTool:
    """Exam tools exposed to the application/AI orchestration layer."""

    name = "exams"

    @staticmethod
    def execute(user_id: int) -> dict[str, Any]:
        """Get exam information for the authenticated user."""

        return ExamService.get_exams(user_id)