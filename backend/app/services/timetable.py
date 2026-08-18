from typing import Any


class TimetableService:
    """Mock school timetable service.

    This layer represents the school ERP/mock API.
    It contains no LLM logic and no authorization decisions.
    """

    @staticmethod
    def get_timetable(user_id: int) -> dict[str, Any]:
        """Return the timetable for the authenticated user."""

        # Mock ERP response for development.
        return {
            "user_id": user_id,
            "day": "today",
            "timetable": [
                {
                    "period": 1,
                    "subject": "Mathematics",
                    "teacher": "Mr. Sharma",
                    "time": "09:00-09:50",
                },
                {
                    "period": 2,
                    "subject": "Physics",
                    "teacher": "Ms. Das",
                    "time": "10:00-10:50",
                },
                {
                    "period": 3,
                    "subject": "Computer Science",
                    "teacher": "Mr. Kumar",
                    "time": "11:00-11:50",
                },
                {
                    "period": 4,
                    "subject": "English",
                    "teacher": "Mrs. Singh",
                    "time": "12:00-12:50",
                },
            ],
        }