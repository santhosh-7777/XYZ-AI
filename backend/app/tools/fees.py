from typing import Any

from backend.app.services.fees import FeeService


class FeeTool:
    """Fee tools exposed to the application/AI orchestration layer."""

    name = "fees"

    @staticmethod
    def execute(user_id: int) -> dict[str, Any]:
        """Get fee information for the authenticated user."""

        return FeeService.get_fees(user_id)