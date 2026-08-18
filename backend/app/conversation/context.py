from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversationContext:
    """Stores the latest conversation state for one authenticated user."""

    user_id: int

    last_intent: str | None = None
    last_tool: str | None = None
    last_entities: dict[str, Any] = field(default_factory=dict)
    last_result: dict[str, Any] = field(default_factory=dict)

    pending_action_id: str | None = None
    pending_action_intent: str | None = None

    student_name: str | None = None


class ConversationContextStore:
    """
    Small in-memory conversation context store.

    This is intentionally replaceable.
    Production can later move this to Redis/database without
    changing the conversation manager interface.
    """

    _contexts: dict[int, ConversationContext] = {}

    @classmethod
    def get(cls, user_id: int) -> ConversationContext:
        """Get existing context or create a new one."""

        if user_id not in cls._contexts:
            cls._contexts[user_id] = ConversationContext(
                user_id=user_id
            )

        return cls._contexts[user_id]

    @classmethod
    def update(
        cls,
        user_id: int,
        intent: str | None = None,
        tool: str | None = None,
        entities: dict[str, Any] | None = None,
        result: dict[str, Any] | None = None,
        pending_action_id: str | None = None,
        pending_action_intent: str | None = None,
    ) -> ConversationContext:
        """Update the user's latest conversation state."""

        context = cls.get(user_id)

        if intent is not None:
            context.last_intent = intent

        if tool is not None:
            context.last_tool = tool

        if entities is not None:
            context.last_entities = dict(entities)

            student_name = entities.get("student_name")

            if student_name:
                context.student_name = student_name

        if result is not None:
            context.last_result = dict(result)

        if pending_action_id is not None:
            context.pending_action_id = pending_action_id

        if pending_action_intent is not None:
            context.pending_action_intent = pending_action_intent

        return context

    @classmethod
    def clear_pending_action(cls, user_id: int) -> None:
        """Remove the pending confirmation action."""

        context = cls.get(user_id)

        context.pending_action_id = None
        context.pending_action_intent = None

    @classmethod
    def clear(cls, user_id: int) -> None:
        """Clear all conversation context for a user."""

        cls._contexts.pop(user_id, None)