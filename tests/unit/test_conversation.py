from backend.app.conversation.context import ConversationContextStore
from backend.app.conversation.manager import (
    ConversationManager,
    is_confirmation_message,
    is_correction_message,
    requires_previous_context,
)


def setup_function():
    """Start every test with a clean conversation store."""
    ConversationContextStore._contexts.clear()


def test_parent_child_context_is_remembered():
    ConversationContextStore.update(
        3,
        intent="CHILD_ATTENDANCE",
        tool="get_child_attendance",
        entities={"student_name": "Rahul"},
        result={
            "attendance_percentage": 91.2,
        },
    )

    context = ConversationManager.get_context(3)

    assert context.last_intent == "CHILD_ATTENDANCE"
    assert context.last_tool == "get_child_attendance"
    assert context.student_name == "Rahul"


def test_parent_follow_up_last_month_uses_previous_child_context():
    ConversationContextStore.update(
        3,
        intent="CHILD_ATTENDANCE",
        tool="get_child_attendance",
        entities={"student_name": "Rahul"},
        result={
            "attendance_percentage": 91.2,
        },
    )

    result = ConversationManager.resolve_follow_up(
        3,
        "How about last month?",
    )

    assert result is not None
    assert result["type"] == "FOLLOW_UP"
    assert result["previous_intent"] == "CHILD_ATTENDANCE"
    assert result["previous_tool"] == "get_child_attendance"
    assert result["entities"]["student_name"] == "Rahul"
    assert result["entities"]["period"] == "last_month"


def test_student_follow_up_uses_previous_attendance_context():
    ConversationContextStore.update(
        1,
        intent="OWN_ATTENDANCE",
        tool="get_my_attendance",
        entities={},
        result={
            "attendance_percentage": 88.5,
        },
    )

    result = ConversationManager.resolve_follow_up(
        1,
        "What about last month?",
    )

    assert result is not None
    assert result["type"] == "FOLLOW_UP"
    assert result["previous_intent"] == "OWN_ATTENDANCE"
    assert result["previous_tool"] == "get_my_attendance"
    assert result["entities"]["period"] == "last_month"


def test_confirmation_message_is_detected():
    assert is_confirmation_message("Yes")
    assert is_confirmation_message("Yes, request the call.")
    assert is_confirmation_message("confirm")


def test_confirmation_requires_pending_action():
    ConversationContextStore.update(
        3,
        intent="ESCALATION",
        tool="create_escalation_request",
        entities={},
        result={
            "status": "CONFIRMATION_REQUIRED",
            "action_id": "action-123",
        },
        pending_action_id="action-123",
        pending_action_intent="ESCALATION",
    )

    result = ConversationManager.resolve_confirmation(
        3,
        "Yes, request the call.",
    )

    assert result is not None
    assert result["type"] == "CONFIRMATION"
    assert result["action_id"] == "action-123"
    assert result["intent"] == "ESCALATION"


def test_confirmation_without_pending_action_returns_none():
    result = ConversationManager.resolve_confirmation(
        3,
        "Yes",
    )

    assert result is None


def test_ambiguous_request_can_be_identified_as_correction_or_normal_message():
    assert is_correction_message(
        "No, I meant my timetable."
    )

    assert not is_correction_message(
        "How is Rahul doing?"
    )


def test_context_required_without_previous_context():
    result = ConversationManager.resolve_follow_up(
        1,
        "Can you check it?",
    )

    assert result is not None
    assert result["type"] == "CONTEXT_REQUIRED"
    assert "context" in result["message"].lower()


def test_follow_up_detection():
    assert requires_previous_context("How about last month?")
    assert requires_previous_context("What about last month?")
    assert requires_previous_context("Can you check it?")


def test_correction_message_detection():
    assert is_correction_message(
        "No, I meant my timetable."
    )

    assert is_correction_message(
        "Actually, I meant my timetable."
    )

    assert is_correction_message(
        "Instead, show my timetable."
    )


def test_pending_action_is_cleared():
    ConversationContextStore.update(
        3,
        intent="ESCALATION",
        tool="create_escalation_request",
        entities={},
        result={},
        pending_action_id="action-123",
        pending_action_intent="ESCALATION",
    )

    context = ConversationManager.get_context(3)

    assert context.pending_action_id == "action-123"

    ConversationManager.clear_pending_action(3)

    context = ConversationManager.get_context(3)

    assert context.pending_action_id is None
    assert context.pending_action_intent is None