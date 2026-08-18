from typing import Any

from backend.app.services.academic_performance import AcademicPerformanceService


class AcademicPerformanceTool:
    """Academic performance tools exposed to the application/AI orchestration layer."""

    name = "academic_performance"

    @staticmethod
    def execute(user_id: int) -> dict[str, Any]:
        """Get academic performance information for the authenticated user."""

        return AcademicPerformanceService.get_performance(user_id)