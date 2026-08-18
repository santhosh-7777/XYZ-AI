from typing import Any


class FeeService:
    """Mock school fee service.

    This layer represents the school ERP/mock API.
    It contains no LLM logic and no authorization decisions.
    """

    @staticmethod
    def get_fees(user_id: int) -> dict[str, Any]:
        """Return fee information for the authenticated user."""

        return {
            "user_id": user_id,
            "total_fees": 75000.0,
            "paid_amount": 60000.0,
            "pending_amount": 15000.0,
            "currency": "INR",
            "status": "PARTIALLY_PAID",
        }