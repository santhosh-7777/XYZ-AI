from typing import Any


class AssignmentService:
    """Mock assignment service.

    This layer represents the school ERP/mock API.
    It contains no LLM logic and no authorization decisions.
    """

    @staticmethod
    def get_assignments(user_id: int) -> dict[str, Any]:
        """Return pending assignment information for the authenticated user."""

        return {
            "user_id": user_id,
            "assignments": [
                {
                    "subject": "Mathematics",
                    "title": "Chapter 5 Problem Set",
                    "due_date": "2026-08-25",
                    "status": "PENDING",
                },
                {
                    "subject": "English",
                    "title": "Essay: My Summer Vacation",
                    "due_date": "2026-08-22",
                    "status": "PENDING",
                },
                {
                    "subject": "Computer Science",
                    "title": "Lab Assignment 3",
                    "due_date": "2026-08-28",
                    "status": "SUBMITTED",
                },
            ],
        }