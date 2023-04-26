from __future__ import annotations

import typing

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
        @bp.route("/substitutions/date/<date:date>")
        def get_substitutions(date: datetime.date) -> list[dict[str, Any]]:
            return list(Entity.get_substitutions(date))

        @bp.route("/substitutions/date/<date:date>/classes/<list:classes>")
        def get_substitutions_for_classes(
            date: datetime.date,
            classes: list[str],
        ) -> list[dict[str, Any]]:
            return list(Class.get_substitutions(date, classes))

        @bp.route("/substitutions/date/<date:date>/teachers/<list:teachers>")
        def get_substitutions_for_teachers(
            date: datetime.date,
            teachers: list[str],
        ) -> list[dict[str, Any]]:
            return list(Teacher.get_substitutions(date, teachers))

        @bp.route("/substitutions/date/<date:date>/classrooms/<list:classrooms>")
        def get_substitutions_for_classrooms(
            date: datetime.date,
            classrooms: list[str],
        ) -> list[dict[str, Any]]:
            return list(Classroom.get_substitutions(date, classrooms))
