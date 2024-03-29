from __future__ import annotations

import typing

from .base import BaseHandler
from ..database import Class, Classroom, Entity, Teacher

if typing.TYPE_CHECKING:
    from typing import Any
    from flask import Blueprint
    from ..config import Config


class TimetableHandler(BaseHandler):
    name = "timetable"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        @bp.route("/timetable")
        def get_timetable() -> list[dict[str, Any]]:
            return list(Entity.get_lessons())

        @bp.route("/timetable/classes/<list:classes>")
        def get_timetable_for_classes(classes: list[str]) -> list[dict[str, Any]]:
            return list(Class.get_lessons(classes))

        @bp.route("/timetable/teachers/<list:teachers>")
        def get_timetable_for_teachers(teachers: list[str]) -> list[dict[str, Any]]:
            return list(Teacher.get_lessons(teachers))

        @bp.route("/timetable/classrooms/<list:classrooms>")
        def get_timetable_for_classrooms(classrooms: list[str]) -> list[dict[str, Any]]:
            return list(Classroom.get_lessons(classrooms))

        @bp.route("/timetable/classrooms/empty")
        def get_timetable_for_empty_classrooms() -> list[dict[str, Any]]:
            return list(Classroom.get_empty())
