import re
from typing import Any

from backend.app.conversation.context import (
    ConversationContext,
    ConversationContextStore,
)


# ---------------------------------------------------------
# MESSAGE CLASSIFICATION HELPERS
# ---------------------------------------------------------

def is_confirmation_message(text: str) -> bool:
    """
    Detect explicit confirmation messages.

    Examples:
        Yes
        Yes, request the call.
        Confirm
        Please confirm
        Do it
    """

    normalized = text.strip().lower()

    patterns = [
        r"^yes$",
        r"^yes[,.! ]+.*",
        r"^confirm$",
        r"^confirmed$",
        r"^please confirm$",
        r"^do it$",
        r"^go ahead$",
        r"^approve$",
        r"^approved$",
        r"^sure$",
    ]

    return any(
        re.match(pattern, normalized)
        for pattern in patterns
    )


def is_correction_message(text: str) -> bool:
    """
    Detect when the user corrects their previous request.

    Examples:
        No, I meant my timetable.
        Actually, I meant my timetable.
        Instead, show my timetable.
    """

    normalized = text.strip().lower()

    correction_patterns = [
        r"^no[, ]+i meant\b",
        r"^no[, ]+i mean\b",
        r"^actually[, ]+i meant\b",
        r"^actually[, ]+i mean\b",
        r"^instead[, ]+",
        r"^i meant\b",
        r"^i mean\b",
        r"^correction[, ]+",
    ]

    return any(
        re.search(pattern, normalized)
        for pattern in correction_patterns
    )


def requires_previous_context(text: str) -> bool:
    """
    Detect messages that cannot be fully understood without
    the previous conversation turn.
    """

    normalized = text.strip().lower()

    follow_up_patterns = [
        r"\bhow about last month\b",
        r"\bwhat about last month\b",
        r"\blast month\b",
        r"\bwhat about\b",
        r"\bhow about\b",
        r"\bcan you check it\b",
        r"\bcheck it\b",
        r"\bwhat about that\b",
        r"\bhow about that\b",
        r"\bwhat about this\b",
        r"\bhow about this\b",
    ]

    return any(
        re.search(pattern, normalized)
        for pattern in follow_up_patterns
    )


# ---------------------------------------------------------
# CONVERSATION MANAGER
# ---------------------------------------------------------

class ConversationManager:
    """
    Handles lightweight conversation state.

    Responsibilities:

    1. Remember previous intent/tool/entities.
    2. Resolve follow-up requests.
    3. Detect missing context.
    4. Detect confirmation messages.
    5. Detect corrections.
    """

    @staticmethod
    def get_context(user_id: int) -> ConversationContext:
        return ConversationContextStore.get(user_id)

    @staticmethod
    def save_result(
        user_id: int,
        intent: str,
        tool: str | None,
        entities: dict[str, Any],
        result: dict[str, Any],
    ) -> ConversationContext:

        return ConversationContextStore.update(
            user_id=user_id,
            intent=intent,
            tool=tool,
            entities=entities,
            result=result,
        )

    # -----------------------------------------------------
    # FOLLOW-UP
    # -----------------------------------------------------

    @staticmethod
    def resolve_follow_up(
        user_id: int,
        text: str,
    ) -> dict[str, Any] | None:

        if not requires_previous_context(text):
            return None

        context = ConversationContextStore.get(user_id)

        # No previous context available.
        if context.last_intent is None:
            return {
                "type": "CONTEXT_REQUIRED",
                "message": (
                    "I need a little more context. "
                    "What would you like me to check?"
                ),
            }

        normalized = text.strip().lower()

        entities = dict(context.last_entities)

        # Preserve the student from previous conversation.
        if context.student_name:
            entities["student_name"] = context.student_name

        # Detect period.
        if "last month" in normalized:
            entities["period"] = "last_month"

        return {
            "type": "FOLLOW_UP",
            "previous_intent": context.last_intent,
            "previous_tool": context.last_tool,
            "entities": entities,
        }

    # -----------------------------------------------------
    # CONFIRMATION
    # -----------------------------------------------------

    @staticmethod
    def resolve_confirmation(
        user_id: int,
        text: str,
    ) -> dict[str, Any] | None:

        if not is_confirmation_message(text):
            return None

        context = ConversationContextStore.get(user_id)

        if context.pending_action_id is None:
            return None

        return {
            "type": "CONFIRMATION",
            "action_id": context.pending_action_id,
            "intent": context.pending_action_intent,
        }

    # -----------------------------------------------------
    # CLEAR PENDING ACTION
    # -----------------------------------------------------

    @staticmethod
    def clear_pending_action(user_id: int) -> None:
        ConversationContextStore.clear_pending_action(user_id)

    # -----------------------------------------------------
    # CORRECTION
    # -----------------------------------------------------

    @staticmethod
    def resolve_correction(
        user_id: int,
        text: str,
    ) -> dict[str, Any] | None:

        if not is_correction_message(text):
            return None

        return {
            "type": "CORRECTION",
            "message": text.strip(),
        }