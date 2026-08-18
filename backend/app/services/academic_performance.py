from typing import Any


class AcademicPerformanceService:
    """Mock academic performance service.

    This layer represents the school ERP/mock API.
    It contains no LLM logic and no authorization decisions.
    """

    @staticmethod
    def get_performance(user_id: int) -> dict[str, Any]:
        """Return academic performance information for the authenticated user."""

        return {
            "user_id": user_id,
            "overall_grade": "A",
            "gpa": 8.7,
            "subjects": [
                {"subject": "Mathematics", "grade": "A", "marks": 92},
                {"subject": "Physics", "grade": "A-", "marks": 87},
                {"subject": "Computer Science", "grade": "A+", "marks": 96},
                {"subject": "English", "grade": "B+", "marks": 82},
            ],
        }