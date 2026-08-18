from typing import Any


class AttendanceService:
    """Mock school attendance service.

    This layer represents the school ERP/mock API.
    It contains no LLM logic and no authorization decisions.
    """

    @staticmethod
    def get_my_attendance(user_id: int) -> dict[str, Any]:
        """Return attendance for the authenticated student."""

        # Mock ERP response for development.
        return {
            "student_id": user_id,
            "student_name": "Student",
            "attendance_percentage": 91.2,
            "present_days": 114,
            "absent_days": 11,
            "total_days": 125,
        }

    @staticmethod
    def get_child_attendance(
        parent_user_id: int,
        child_id: int,
    ) -> dict[str, Any]:
        """Return attendance for a child authorized to the parent."""

        # Mock ERP response.
        # Real child-resource authorization will be enforced
        # by the application/RBAC layer before this service is called.
        return {
            "parent_user_id": parent_user_id,
            "student_id": child_id,
            "student_name": "Rahul",
            "attendance_percentage": 91.2,
            "present_days": 114,
            "absent_days": 11,
            "total_days": 125,
        }

    @staticmethod
    def get_attendance_history(
        student_id: int,
        period: str,
    ) -> dict[str, Any]:
        """Return attendance history for a student."""

        # Mock ERP response for development.
        return {
            "student_id": student_id,
            "student_name": "Rahul" if student_id == 101 else "Student",
            "period": period,
            "attendance_percentage": 89.5,
            "present_days": 34,
            "absent_days": 4,
            "total_days": 38,
        }

    @staticmethod
    def mark_attendance(
        teacher_user_id: int,
        student_id: int,
        student_name: str,
        date: str,
        status: str,
    ) -> dict[str, Any]:
        """Mock attendance mutation for an authorized teacher."""

        return {
            "teacher_user_id": teacher_user_id,
            "student_id": student_id,
            "student_name": student_name,
            "date": date,
            "status": status,
            "updated": True,
        }

    @staticmethod
    def get_school_analytics() -> dict[str, Any]:
        """Return school-wide attendance analytics for principals."""

        # Mock ERP response.
        return {
            "school_attendance_percentage": 92.4,
            "total_students": 480,
            "present_today": 443,
            "absent_today": 37,
            "classes_below_threshold": ["8-B", "9-C"],
        }