# Maps parent user_id -> their child's student_id and name.
# Mock/demo mapping - replace with a real DB relationship later.
PARENT_TO_CHILD: dict[int, dict[str, int | str]] = {
    3: {"student_id": 101, "student_name": "Rahul"},  # parent@test.com -> Rahul
    6: {"student_id": 101, "student_name": "Rahul"},  # parent1@test.com -> Rahul
}


def resolve_child(parent_user_id: int) -> dict[str, int | str] | None:
    return PARENT_TO_CHILD.get(parent_user_id)