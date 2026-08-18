from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any


STATUS_MAP = {
    "absent": "ABSENT",
    "present": "PRESENT",
    "गैरहाज़िर": "ABSENT",
    "अनुपस्थित": "ABSENT",
    "उपस्थित": "PRESENT",
    "గైర్హాజరు": "ABSENT",
    "హాజరు": "PRESENT",
    "வரவில்லை": "ABSENT",
    "வருகை": "PRESENT",
}

DATE_MAP = {
    "today": 0,
    "tomorrow": 1,
    "आज": 0,
    "कल": 1,
    "ఈరోజు": 0,
    "రేపు": 1,
    "இன்று": 0,
    "நாளை": 1,
}

# Canonical student name -> known spellings/transliterations/inflected forms.
# Extend this per real student in your mock DB.
STUDENT_ALIASES: dict[str, list[str]] = {
    "Rahul": [
        "rahul",
        "राहुल",
        "రాహుల్", "రాహుల్‌ని", "రాహుల్‌ను",
        "ராகுல்", "ராகுலை", "ராகுலின்",
    ],
}

# Build a flat lookup: any known variant (lowercased) -> canonical name.
# Sorted longest-first so inflected forms (e.g. "ராகுலை") match before
# shorter stems that might also be substrings.
_NAME_LOOKUP: list[tuple[str, str]] = sorted(
    (
        (variant.lower(), canonical)
        for canonical, variants in STUDENT_ALIASES.items()
        for variant in variants
    ),
    key=lambda pair: len(pair[0]),
    reverse=True,
)


def _extract_student_name(text: str, lowered: str) -> str | None:
    # 1. Try alias table first - works across all scripts and known
    #    inflected forms.
    for variant, canonical in _NAME_LOOKUP:
        if variant in lowered:
            return canonical

    # 2. Fallback: English action-phrase regex for names not yet
    #    in the alias table (Latin script only).
    match = re.search(
        r"\b(?:mark|set|check|show|for)\s+([A-Z][a-z]+)\b",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).capitalize()

    return None


def extract_entities(
    text: str,
    reference_date: date | None = None,
) -> dict[str, Any]:
    """Extract and normalize entities required by school actions."""

    if reference_date is None:
        reference_date = date.today()

    normalized = text.strip()
    lowered = normalized.lower()

    result: dict[str, Any] = {
        "student_name": None,
        "date": None,
        "status": None,
    }

    for phrase, canonical in STATUS_MAP.items():
        if phrase.lower() in lowered:
            result["status"] = canonical
            break

    for phrase, offset in DATE_MAP.items():
        if phrase.lower() in lowered:
            result["date"] = (reference_date + timedelta(days=offset)).isoformat()
            break

    result["student_name"] = _extract_student_name(normalized, lowered)

    return result