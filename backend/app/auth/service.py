from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.role import Role
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, RegisterRequest
from backend.app.security.jwt import create_access_token
from backend.app.security.password import hash_password, verify_password


class AuthService:
    @staticmethod
    def register(db: Session, data: RegisterRequest) -> User:
        existing_user = db.scalar(
            select(User).where(User.email == str(data.email).lower())
        )

        if existing_user is not None:
            raise ValueError("Email is already registered")

        role_name = data.role.strip().upper()

        role = db.scalar(
            select(Role).where(Role.name == role_name)
        )

        if role is None:
            raise ValueError("Invalid role")

        user = User(
            email=str(data.email).lower(),
            password_hash=hash_password(data.password),
            role_id=role.id,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def login(db: Session, data: LoginRequest) -> tuple[User, str]:
        user = db.scalar(
            select(User).where(User.email == str(data.email).lower())
        )

        if user is None or not verify_password(
            data.password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is inactive")

        role = db.get(Role, user.role_id)

        if role is None:
            raise ValueError("User role not found")

        token = create_access_token(
            user_id=user.id,
            role=role.name,
        )

        return user, token