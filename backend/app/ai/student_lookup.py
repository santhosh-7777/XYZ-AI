# Maps known student names (from entity extraction) to their DB IDs.
# Mock/demo mapping - extend or replace with a real DB query later.
STUDENT_NAME_TO_ID: dict[str, int] = {
    "Rahul": 101,
}


def resolve_student_id(student_name: str | None) -> int | None:
    if student_name is None:
        return None
    return STUDENT_NAME_TO_ID.get(student_name)