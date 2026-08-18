from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4


@dataclass
class PendingAction:
    """A state-changing action waiting for explicit user confirmation."""

    action_id: str
    user_id: int
    intent: str
    tool: str
    arguments: dict[str, Any]
    expires_at: datetime


class ConfirmationService:
    """In-memory confirmation manager.

    This is intentionally small and replaceable.
    Production deployments can later move this state to Redis/database
    without changing the calling code.
    """

    _pending: dict[str, PendingAction] = {}
    _ttl_seconds = 300

    @classmethod
    def create_pending_action(
        cls,
        user_id: int,
        intent: str,
        tool: str,
        arguments: dict[str, Any],
    ) -> PendingAction:
        action = PendingAction(
            action_id=str(uuid4()),
            user_id=user_id,
            intent=intent,
            tool=tool,
            arguments=arguments,
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=cls._ttl_seconds),
        )

        cls._pending[action.action_id] = action
        return action

    @classmethod
    def get_pending_action(
        cls,
        action_id: str,
        user_id: int,
    ) -> PendingAction | None:
        action = cls._pending.get(action_id)

        if action is None:
            return None

        if action.user_id != user_id:
            return None

        if action.expires_at <= datetime.now(timezone.utc):
            cls._pending.pop(action_id, None)
            return None

        return action

    @classmethod
    def consume_pending_action(
        cls,
        action_id: str,
        user_id: int,
    ) -> PendingAction | None:
        action = cls.get_pending_action(action_id, user_id)

        if action is None:
            return None

        # One-time use: prevent replaying the same confirmation.
        cls._pending.pop(action_id, None)

        return action