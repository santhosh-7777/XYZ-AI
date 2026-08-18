from typing import Any

from backend.app.services.attendance import AttendanceService


class AttendanceTool:
    """Attendance tools exposed to the application/AI orchestration layer."""

    name = "attendance"

    @staticmethod
    def execute(user_id: int) -> dict[str, Any]:
        """Get attendance for the authenticated student."""
        return AttendanceService.get_my_attendance(user_id)

    @staticmethod
    def get_child_attendance(
        parent_user_id: int,
        child_id: int,
    ) -> dict[str, Any]:
        """Get attendance for a parent's authorized child."""
        return AttendanceService.get_child_attendance(
            parent_user_id=parent_user_id,
            child_id=child_id,
        )
    @staticmethod
    def mark_attendance(
        teacher_user_id: int,
        student_id: int,
        student_name: str,
        date: str,
        status: str,
    ) -> dict[str, Any]:
        """Mark attendance through the mock school service."""

        return AttendanceService.mark_attendance(
            teacher_user_id=teacher_user_id,
            student_id=student_id,
            student_name=student_name,
            date=date,
            status=status,
        )

    @staticmethod
    def get_attendance_history(
        student_id: int,
        period: str,
    ) -> dict[str, Any]:
        """Get attendance history for an authorized student."""

        return AttendanceService.get_attendance_history(
            student_id=student_id,
            period=period,
        )