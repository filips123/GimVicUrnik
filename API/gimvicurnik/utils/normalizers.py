from __future__ import annotations

import typing
from datetime import date as date_

from .database import get_or_create
from ..database import Class, Classroom, Teacher

if typing.TYPE_CHECKING:
    from typing import Any
    from sqlalchemy.orm import Session


def normalize_subject_name(name: str) -> str | None:
    """Normalize the subject name."""

    # Special case: Unknown subject
    if is_name_empty(name):
        return None

    # Special case: Subject aliases
    if name == "ŠVZS":
        return "ŠVZ"
    elif name == "ŠPVF":
        return "ŠVM"
    elif name == "ŠPVD":
        return "ŠVŽ"

    # Return the normal name
    return name


def normalize_teacher_name(name: str) -> str | None:
    """Normalize the teacher name."""

    # Special case: Additional lesson
    if name == "Po urniku ni pouka":
        return None

    # Special case: No teacher
    if name == "samozaposleni":
        return None

    # Special case: Unknown teacher
    if is_name_empty(name):
        return None

    # Special case: Multiple Krapež teachers
    if "Krapež" in name:
        if "Alenka" in name:
            return "KrapežA"
        elif "Marjetka" in name:
            return "KrapežM"

    # Special case: Multiple Šajn teachers
    if "Šajn" in name:
        if "Eva" in name:
            return "ŠajnE"
        elif "Majda" in name:
            return "ŠajnM"

    # Special case: Teachers with multiple surnames
    teachers = {
        "Crnoja": "Legan",
        "Erbežnik": "Mihelič",
        "Gresl": "Černe",
        "Jereb": "Batagelj",
        "Merhar": "Kariž",
        "Osole": "Pikl",
        "Stjepić": "ŠajnM",
        "Tehovnik": "Glaser",
        "Vahtar": "Rudolf",
        "Potočnik": "Vičar",
        "Završnik": "Ražen",
        "Zelič": "Ocvirk",
        "Žemva": "Strmčnik",
    }
    if name.split()[0] in teachers:
        return teachers[name.split()[0]]

    # Use only surname
    return name.split()[0]


def normalize_classroom_name(name: str) -> str | None:
    """Normalize the classroom name."""

    # Special case: Unknown classroom
    if is_name_empty(name):
        return None

    # Special case: Classroom aliases
    # Maybe these mappings aren't correct, but who knows...
    if name == "Velika dvorana" or name == "Velika telovadnica":
        return "TV1"
    if name == "Mala dvorana" or name == "Mala telovadnica":
        return "TV3"

    # Return the normal name
    return name


def normalize_other_names(name: str) -> str | None:
    """Normalize other types of names."""

    return name if not is_name_empty(name) else None


def is_name_empty(name: str) -> bool:
    """Return whether the name is empty."""

    return not name or name == "X" or name == "x" or name == "/" or name == "MANJKA"


def format_substitution(
    session: Session,
    date: date_,
    day: int,
    time: int,
    subject: str | None,
    notes: str | None,
    original_teacher: str | None,
    original_classroom: str | None,
    class_: str | None,
    teacher: str | None,
    classroom: str | None,
) -> dict[str, Any]:
    """Format the substitution into a dict that can be stored into a database."""

    # fmt: off
    return {
        "date": date,
        "day": day,
        "time": time,
        "subject": subject,
        "notes": notes,
        "original_teacher_id": get_or_create(session, model=Teacher, name=original_teacher)[0].id if original_teacher else None,
        "original_classroom_id": get_or_create(session, model=Classroom, name=original_classroom)[0].id if original_classroom else None,
        "class_id": get_or_create(session, model=Class, name=class_)[0].id if class_ else None,
        "teacher_id": get_or_create(session, model=Teacher, name=teacher)[0].id if teacher else None,
        "classroom_id": get_or_create(session, model=Classroom, name=classroom)[0].id if classroom else None,
    }
    # fmt: on
