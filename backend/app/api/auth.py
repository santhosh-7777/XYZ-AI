from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.auth.service import AuthService
from backend.app.db.session import get_db
from backend.app.models.role import Role
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from backend.app.security.jwt import decode_access_token
from backend.app.security.rbac import require_permission


router = APIRouter(prefix="/auth", tags=["Authentication"])

bearer_scheme = HTTPBearer()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = AuthService.register(db, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    role = db.get(Role, user.role_id)

    return UserResponse(
        id=user.id,
        email=user.email,
        role=role.name,
        is_active=user.is_active,
    )


@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        user, token = AuthService.login(db, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    role = db.get(Role, user.role_id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": role.name,
        },
    }


@router.get("/me", response_model=UserResponse)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = db.get(Role, user.role_id)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User role not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        role=role.name,
        is_active=user.is_active,
    )

@router.get("/test-attendance")
def test_attendance(
    user: User = Depends(require_permission("OWN_ATTENDANCE")),
    db: Session = Depends(get_db),
):
    role = db.get(Role, user.role_id)

    return {
        "message": "Attendance access granted",
        "user_id": user.id,
        "role": role.name,
        "intent": "OWN_ATTENDANCE",
    }
@router.get("/test-mark-attendance")
def test_mark_attendance(
    user: User = Depends(require_permission("MARK_ATTENDANCE")),
    db: Session = Depends(get_db),
):
    role = db.get(Role, user.role_id)

    return {
        "message": "Mark attendance access granted",
        "user_id": user.id,
        "role": role.name,
        "intent": "MARK_ATTENDANCE",
    }