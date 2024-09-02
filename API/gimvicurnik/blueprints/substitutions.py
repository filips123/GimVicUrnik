from __future__ import annotations

import typing

from ..utils.dates import get_weekdays
from .base import BaseHandler
from ..database import Class, Classroom, Entity, Teacher

if typing.TYPE_CHECKING:
    import datetime
    from typing import Any
    from flask import Blueprint
    from ..config import Config


class SubstitutionsHandler(BaseHandler):
    name = "substitutions"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        def _fetch_week_substitutions(
            date: datetime.date,
            entity: type[Entity],
            names: list[str],
        ) -> list[list[dict[str, Any]]]:
            """Fetch substitutions for a week containing the given date."""

            weekdays = get_weekdays(date)
            substitutions = entity.get_substitutions(weekdays, names)

            grouped: dict[str, list[dict[str, Any]]] = {day.isoformat(): [] for day in weekdays}

            for substitution in substitutions:
                grouped[substitution["date"]].append(substitution)

            return list(grouped.values())

        @bp.route("/substitutions/date/<date:date>")
        def get_date_substitutions(date: datetime.date) -> list[dict[str, Any]]:
            return list(Entity.get_substitutions([date]))

        @bp.route("/substitutions/date/<date:date>/classes/<list:classes>")
        def get_date_substitutions_for_classes(
            date: datetime.date,
            classes: list[str],
        ) -> list[dict[str, Any]]:
            return list(Class.get_substitutions([date], classes))

        @bp.route("/substitutions/date/<date:date>/teachers/<list:teachers>")
        def get_date_substitutions_for_teachers(
            date: datetime.date,
            teachers: list[str],
        ) -> list[dict[str, Any]]:
            return list(Teacher.get_substitutions([date], teachers))

        @bp.route("/substitutions/date/<date:date>/classrooms/<list:classrooms>")
        def get_date_substitutions_for_classrooms(
            date: datetime.date,
            classrooms: list[str],
        ) -> list[dict[str, Any]]:
            return list(Classroom.get_substitutions([date], classrooms))

        @bp.route("/substitutions/week/<date:date>")
        def get_week_substitutions(date: datetime.date) -> list[list[dict[str, Any]]]:
            return _fetch_week_substitutions(date, Entity, [])

        @bp.route("/substitutions/week/<date:date>/classes/<list:classes>")
        def get_week_substitutions_for_classes(
            date: datetime.date,
            classes: list[str],
        ) -> list[list[dict[str, Any]]]:
            return _fetch_week_substitutions(date, Class, classes)

        @bp.route("/substitutions/week/<date:date>/teachers/<list:teachers>")
        def get_week_substitutions_for_teachers(
            date: datetime.date,
            teachers: list[str],
        ) -> list[list[dict[str, Any]]]:
            return _fetch_week_substitutions(date, Teacher, teachers)

        @bp.route("/substitutions/week/<date:date>/classrooms/<list:classrooms>")
        def get_week_substitutions_for_classrooms(
            date: datetime.date,
            classrooms: list[str],
        ) -> list[list[dict[str, Any]]]:
            return _fetch_week_substitutions(date, Classroom, classrooms)
