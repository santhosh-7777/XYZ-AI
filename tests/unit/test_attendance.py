from backend.app.services.attendance import AttendanceService
from backend.app.tools.attendance import AttendanceTool


def test_get_my_attendance():
    result = AttendanceService.get_my_attendance(1)

    assert result["student_id"] == 1
    assert result["attendance_percentage"] == 91.2
    assert result["present_days"] == 114
    assert result["absent_days"] == 11
    assert result["total_days"] == 125


def test_get_child_attendance():
    result = AttendanceService.get_child_attendance(
        parent_user_id=2,
        child_id=101,
    )

    assert result["parent_user_id"] == 2
    assert result["student_id"] == 101
    assert result["student_name"] == "Rahul"
    assert result["attendance_percentage"] == 91.2


def test_mark_attendance():
    result = AttendanceService.mark_attendance(
        teacher_user_id=3,
        student_id=101,
        student_name="Rahul",
        date="2026-08-17",
        status="ABSENT",
    )

    assert result["teacher_user_id"] == 3
    assert result["student_id"] == 101
    assert result["student_name"] == "Rahul"
    assert result["date"] == "2026-08-17"
    assert result["status"] == "ABSENT"
    assert result["updated"] is True


def test_attendance_tool_own_attendance():
    result = AttendanceTool.execute(1)

    assert result["student_id"] == 1
    assert result["attendance_percentage"] == 91.2


def test_attendance_tool_child_attendance():
    result = AttendanceTool.get_child_attendance(2, 101)

    assert result["parent_user_id"] == 2
    assert result["student_id"] == 101


def test_attendance_tool_mark_attendance():
    result = AttendanceTool.mark_attendance(
        teacher_user_id=3,
        student_id=101,
        student_name="Rahul",
        date="2026-08-17",
        status="ABSENT",
    )

    assert result["teacher_user_id"] == 3
    assert result["student_id"] == 101
    assert result["updated"] is True