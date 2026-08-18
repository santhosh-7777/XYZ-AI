from typing import Any


class ExamService:
    """Mock exam service.

    This layer represents the school ERP/mock API.
    It contains no LLM logic and no authorization decisions.
    """

    @staticmethod
    def get_exams(user_id: int) -> dict[str, Any]:
        """Return upcoming exam information for the authenticated user."""

        return {
            "user_id": user_id,
            "exams": [
                {
                    "subject": "Mathematics",
                    "date": "2026-09-10",
                    "time": "09:00",
                    "syllabus": "Chapters 1-6",
                },
                {
                    "subject": "Physics",
                    "date": "2026-09-12",
                    "time": "09:00",
                    "syllabus": "Chapters 1-4",
                },
                {
                    "subject": "Computer Science",
                    "date": "2026-09-15",
                    "time": "09:00",
                    "syllabus": "Chapters 1-5",
                },
            ],
        }