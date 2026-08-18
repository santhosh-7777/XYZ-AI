from datetime import datetime, timedelta, timezone

from backend.app.core.confirmation import ConfirmationService


def test_create_pending_action():
    action = ConfirmationService.create_pending_action(
        user_id=3,
        intent="MARK_ATTENDANCE",
        tool="mark_attendance",
        arguments={
            "student_id": 101,
            "student_name": "Rahul",
            "date": "2026-08-17",
            "status": "ABSENT",
        },
    )

    assert action.action_id
    assert action.user_id == 3
    assert action.intent == "MARK_ATTENDANCE"
    assert action.tool == "mark_attendance"
    assert action.arguments["student_id"] == 101


def test_get_pending_action_returns_action_for_owner():
    action = ConfirmationService.create_pending_action(
        user_id=3,
        intent="MARK_ATTENDANCE",
        tool="mark_attendance",
        arguments={"student_id": 101},
    )

    found = ConfirmationService.get_pending_action(
        action.action_id,
        user_id=3,
    )

    assert found is not None
    assert found.action_id == action.action_id


def test_pending_action_cannot_be_accessed_by_another_user():
    action = ConfirmationService.create_pending_action(
        user_id=3,
        intent="MARK_ATTENDANCE",
        tool="mark_attendance",
        arguments={"student_id": 101},
    )

    found = ConfirmationService.get_pending_action(
        action.action_id,
        user_id=999,
    )

    assert found is None


def test_consume_pending_action_is_one_time():
    action = ConfirmationService.create_pending_action(
        user_id=3,
        intent="MARK_ATTENDANCE",
        tool="mark_attendance",
        arguments={"student_id": 101},
    )

    consumed = ConfirmationService.consume_pending_action(
        action.action_id,
        user_id=3,
    )

    assert consumed is not None
    assert consumed.action_id == action.action_id

    replay = ConfirmationService.get_pending_action(
        action.action_id,
        user_id=3,
    )

    assert replay is None


def test_expired_action_is_rejected():
    action = ConfirmationService.create_pending_action(
        user_id=3,
        intent="MARK_ATTENDANCE",
        tool="mark_attendance",
        arguments={"student_id": 101},
    )

    action.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    found = ConfirmationService.get_pending_action(
        action.action_id,
        user_id=3,
    )

    assert found is None