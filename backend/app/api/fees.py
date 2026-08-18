from typing import Any

from fastapi import APIRouter, Depends

from backend.app.models.user import User
from backend.app.security.rbac import require_permission
from backend.app.tools.fees import FeeTool


router = APIRouter(prefix="/fees", tags=["Fees"])


@router.get("/me")
def get_my_fees(
    user: User = Depends(require_permission("FEES")),
) -> dict[str, Any]:
    """Return fee information for the authenticated user."""

    return FeeTool.execute(user.id)