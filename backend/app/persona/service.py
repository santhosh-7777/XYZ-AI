from __future__ import annotations

from typing import Any

from backend.app.llm.response_generator import ResponseGenerator


PERSONA_CATALOG: dict[str, dict[str, Any]] = {
    "STUDENT": {
        "persona_name": "Friendly Academic Assistant",
        "tone": "supportive, concise, encouraging",
        "audience": "student",
    },
    "PARENT": {
        "persona_name": "Caring Parent Support Assistant",
        "tone": "patient, reassuring, clear",
        "audience": "parent",
    },
    "TEACHER": {
        "persona_name": "Professional Teaching Assistant",
        "tone": "professional, efficient, action-oriented",
        "audience": "teacher",
    },
    "PRINCIPAL": {
        "persona_name": "Professional Management Assistant",
        "tone": "formal, analytical, concise",
        "audience": "principal",
    },
}


class PersonaService:
    """
    Role-specific response presentation layer.

    Authorization and tool execution remain outside this class.

    Grok is used only to turn VERIFIED backend results into
    natural, role-aware, multilingual responses.

    Existing deterministic responses remain as a fallback.
    """

    _llm: ResponseGenerator | None = None

    @staticmethod
    def get_persona(role: str) -> dict[str, Any]:
        """Return the persona configuration for a role."""

        persona = PERSONA_CATALOG.get(role.upper())

        if persona is None:
            raise ValueError(f"Unsupported role: {role}")

        return persona

    @classmethod
    def _get_llm(cls) -> ResponseGenerator:
        """
        Lazily create the LLM client.

        This prevents the backend from failing during startup
        if the API key is temporarily unavailable.
        """

        if cls._llm is None:
            cls._llm = ResponseGenerator()

        return cls._llm

    @classmethod
    def _generate_llm_response(
        cls,
        role: str,
        intent: str,
        result: dict[str, Any],
        language: str,
    ) -> str | None:
        """
        Try to generate a natural multilingual response.

        Returns None if Grok is unavailable so that the
        deterministic fallback can still answer the request.
        """

        try:
            return cls._get_llm().generate(
                role=role,
                language=language,
                intent=intent,
                result=result,
            )
        except Exception:
            return None

    @classmethod
    def format_response(
        cls,
        role: str,
        intent: str,
        result: dict[str, Any],
        language: str = "en",
    ) -> str:
        """Format a result according to role, intent and language."""

        role = role.upper()
        intent = intent.upper()
        language = language.lower().strip()

        cls.get_persona(role)

        # =====================================================
        # SECURITY-SENSITIVE / CONTROL FLOW RESPONSES
        # Keep these deterministic.
        # =====================================================

        if intent == "CONTEXT_REQUIRED":
            return result.get(
                "message",
                "I need a little more context. "
                "What would you like me to check?",
            )

        if intent == "CLARIFICATION_REQUIRED":
            return result.get(
                "message",
                "Could you provide a little more information "
                "so I can help you?",
            )

        if intent == "CONFIRMATION_REQUIRED":
            return result.get(
                "message",
                "Please confirm this action.",
            )

        if intent == "ESCALATION":
            if result.get("status") == "CONFIRMATION_REQUIRED":
                return result.get(
                    "message",
                    "Please confirm the escalation request.",
                )

            if result.get("status") == "SUBMITTED":
                request_id = result.get("request_id")

                if request_id:
                    return (
                        "Your escalation request has been submitted. "
                        f"Request ID: {request_id}."
                    )

                return (
                    "Your escalation request has been submitted."
                )

        if intent == "MARK_ATTENDANCE":
            if result.get("status") == "CONFIRMATION_REQUIRED":
                return result.get(
                    "message",
                    "Please confirm this attendance update.",
                )

            student_name = result.get(
                "student_name",
                "The student",
            )

            attendance_status = result.get(
                "status",
                "",
            ).lower()

            attendance_date = result.get(
                "date",
                "the requested date",
            )

            # Only allow Grok to phrase a confirmed action.
            llm_response = cls._generate_llm_response(
                role=role,
                intent=intent,
                result=result,
                language=language,
            )

            if llm_response:
                return llm_response

            return (
                f"{student_name} was marked "
                f"{attendance_status} "
                f"on {attendance_date}."
            )

        # =====================================================
        # SAFE NATURAL-LANGUAGE RESPONSES
        # =====================================================

        llm_response = cls._generate_llm_response(
            role=role,
            intent=intent,
            result=result,
            language=language,
        )

        if llm_response:
            return llm_response

        # =====================================================
        # DETERMINISTIC FALLBACKS
        # =====================================================

        if intent == "GREETING":
            if role == "STUDENT":
                return (
                    "Hi! I'm your academic assistant. "
                    "I can help with attendance, academics, "
                    "assignments, exams, and other school-related "
                    "questions. What can I help you with?"
                )

            if role == "PARENT":
                return (
                    "Hello! I'm here to help with your child's "
                    "school information and support. "
                    "What would you like to check?"
                )

            if role == "TEACHER":
                return (
                    "Hello. I can help with attendance, academic "
                    "information, schedules, and teaching-related "
                    "requests. How can I assist you?"
                )

            if role == "PRINCIPAL":
                return (
                    "Hello. I can assist with school-level "
                    "information, academic data, attendance, "
                    "and management requests. How may I help?"
                )

        if intent == "GENERAL_HELP":
            if role == "STUDENT":
                return (
                    "I can help you with your attendance, timetable, "
                    "exams, assignments, academic performance, "
                    "and school announcements."
                )

            if role == "PARENT":
                return (
                    "I can help you with your child's attendance, "
                    "timetable, exams, assignments, academic "
                    "performance, fees, announcements, and "
                    "human support requests."
                )

            if role == "TEACHER":
                return (
                    "I can help with attendance, timetable, exams, "
                    "assignments, academic performance, "
                    "announcements, and support requests."
                )

            if role == "PRINCIPAL":
                return (
                    "I can help with attendance analytics, "
                    "academic performance, timetable, exams, "
                    "assignments, fees, announcements, and "
                    "management support."
                )

        if intent == "OUT_OF_SCOPE":
            return (
                "I'm XYZ-AI, your school assistant. "
                "I can help with school-related information "
                "and support, but I can't help with that request."
            )

        if intent == "OWN_ATTENDANCE":
            percentage = result.get("attendance_percentage")

            if percentage is not None:
                if role == "STUDENT":
                    return (
                        f"Your current attendance is {percentage}%. "
                        "Keep up the good work!"
                    )

                return f"Your current attendance is {percentage}%."

        if intent == "CHILD_ATTENDANCE":
            student_name = result.get(
                "student_name",
                "Your child",
            )

            percentage = result.get("attendance_percentage")

            if percentage is not None:
                return (
                    f"{student_name} currently has "
                    f"{percentage}% attendance."
                )

        if intent == "ATTENDANCE_HISTORY":
            student_name = result.get(
                "student_name",
                "The student",
            )

            period = result.get(
                "period",
                "the requested period",
            )

            percentage = result.get("attendance_percentage")

            if percentage is not None:
                formatted_period = period.replace("_", " ")

                return (
                    f"{student_name}'s attendance for "
                    f"{formatted_period} was {percentage}%."
                )

        if intent == "TIMETABLE":
            timetable = result.get("timetable", [])

            if not timetable:
                return "No timetable information is available."

            lines = []

            for item in timetable:
                period = item.get("period", "")

                subject = item.get(
                    "subject",
                    "Unknown subject",
                )

                teacher = item.get(
                    "teacher",
                    "Unknown teacher",
                )

                time = item.get("time", "")

                lines.append(
                    f"Period {period}: {subject} "
                    f"with {teacher}"
                    + (f" ({time})" if time else "")
                )

            return (
                "Today's timetable:\n"
                + "\n".join(lines)
            )

        if intent == "SCHOOL_ANALYTICS":
            percentage = result.get(
                "school_attendance_percentage"
            )

            if percentage is None:
                percentage = result.get(
                    "overall_attendance"
                )

            if percentage is not None:
                return (
                    f"The school's overall attendance is "
                    f"{percentage}%."
                )

        if intent == "FEES":
            total = result.get("total_fees")
            paid = result.get("paid_amount")
            pending = result.get("pending_amount")
            currency = result.get("currency", "")
            fee_status = result.get("status", "")

            if total is not None:
                if fee_status == "PARTIALLY_PAID":
                    return (
                        f"You have paid {currency} {paid:,.2f} "
                        f"out of {currency} {total:,.2f}. "
                        f"Pending amount: {currency} {pending:,.2f}."
                    )

                if fee_status == "PAID":
                    return (
                        f"All fees are paid. Total: "
                        f"{currency} {total:,.2f}."
                    )

                return (
                    f"Total fees: {currency} {total:,.2f}, "
                    f"paid: {currency} {paid:,.2f}, "
                    f"pending: {currency} {pending:,.2f}."
                )

        return "I completed the request and received a result."