from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    intent: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    tool: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    authorization_source: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    role = relationship(
        "Role",
        back_populates="permissions",
    )