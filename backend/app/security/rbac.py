from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.permission import Permission
from backend.app.models.role import Role
from backend.app.models.user import User
from backend.app.security.jwt import decode_access_token


bearer_scheme = HTTPBearer()


def require_permission(intent: str):
    def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        # 1. Verify JWT
        try:
            payload = decode_access_token(credentials.credentials)
            user_id = int(payload["sub"])
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        # 2. Load authenticated user
        user = db.scalar(
            select(User).where(User.id == user_id)
        )

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. Load authoritative role from database
        role = db.get(Role, user.role_id)

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not found",
            )

        # 4. Check application-side RBAC policy
        permission = db.scalar(
            select(Permission).where(
                Permission.role_id == role.id,
                Permission.intent == intent,
            )
        )

        # 5. Deny by default
        if permission is None or not permission.allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied for intent: {intent}",
            )

        # 6. Return authenticated user to the protected endpoint
        return user

    return dependency