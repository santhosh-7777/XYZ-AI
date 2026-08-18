from backend.app.persona.service import PersonaService


def test_student_persona():
    persona = PersonaService.get_persona("STUDENT")

    assert persona["persona_name"] == "Friendly Academic Assistant"
    assert persona["tone"] == "supportive, concise, encouraging"
    assert persona["audience"] == "student"


def test_parent_persona():
    persona = PersonaService.get_persona("PARENT")

    assert persona["persona_name"] == "Caring Parent Support Assistant"
    assert persona["tone"] == "patient, reassuring, clear"
    assert persona["audience"] == "parent"


def test_teacher_persona():
    persona = PersonaService.get_persona("TEACHER")

    assert persona["persona_name"] == "Professional Teaching Assistant"
    assert persona["tone"] == "professional, efficient, action-oriented"
    assert persona["audience"] == "teacher"


def test_principal_persona():
    persona = PersonaService.get_persona("PRINCIPAL")

    assert persona["persona_name"] == "Professional Management Assistant"
    assert persona["tone"] == "formal, analytical, concise"
    assert persona["audience"] == "principal"


def test_student_own_attendance_response():
    response = PersonaService.format_response(
        "STUDENT",
        "OWN_ATTENDANCE",
        {"attendance_percentage": 91.2},
    )

    assert "91.2%" in response
    assert "Your" in response


def test_parent_child_attendance_response():
    response = PersonaService.format_response(
        "PARENT",
        "CHILD_ATTENDANCE",
        {
            "student_name": "Rahul",
            "attendance_percentage": 91.2,
        },
    )

    assert "Rahul" in response
    assert "91.2%" in response


def test_teacher_mark_attendance_confirmation_response():
    response = PersonaService.format_response(
        "TEACHER",
        "MARK_ATTENDANCE",
        {
            "status": "CONFIRMATION_REQUIRED",
            "message": "Please confirm marking Rahul absent.",
        },
    )

    assert response == "Please confirm marking Rahul absent."


def test_teacher_mark_attendance_success_response():
    response = PersonaService.format_response(
        "TEACHER",
        "MARK_ATTENDANCE",
        {
            "student_name": "Rahul",
            "status": "ABSENT",
            "date": "2026-08-17",
        },
    )

    assert "Rahul" in response
    assert "absent" in response
    assert "2026-08-17" in response


def test_principal_school_analytics_response():
    response = PersonaService.format_response(
        "PRINCIPAL",
        "SCHOOL_ANALYTICS",
        {
            "overall_attendance": 92.4,
        },
    )

    assert "92.4%" in response


def test_escalation_confirmation_response():
    response = PersonaService.format_response(
        "PARENT",
        "ESCALATION",
        {
            "status": "CONFIRMATION_REQUIRED",
            "message": "Would you like me to submit the request?",
        },
    )

    assert response == "Would you like me to submit the request?"


def test_escalation_submitted_response():
    response = PersonaService.format_response(
        "PARENT",
        "ESCALATION",
        {
            "status": "SUBMITTED",
            "request_id": "ESC-BD467129",
        },
    )

    assert "submitted" in response
    assert "ESC-BD467129" in response


def test_unsupported_role():
    try:
        PersonaService.get_persona("UNKNOWN")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Unsupported role" in str(exc)