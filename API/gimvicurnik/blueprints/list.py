from __future__ import annotations

import typing

from .base import BaseHandler
from ..database import Class, Classroom, Session, Teacher

if typing.TYPE_CHECKING:
    from flask import Blueprint
    from ..config import Config
    from ..database import Entity


class ListHandler(BaseHandler):
    name = "list"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        def _list_entity(entity: type[Entity]) -> list[str]:
            return [model.name for model in Session.query(entity.name).order_by(entity.name)]

        @bp.route("/list/classes")
        def list_classes() -> list[str]:
            return _list_entity(Class)

        @bp.route("/list/teachers")
        def list_teachers() -> list[str]:
            return _list_entity(Teacher)

        @bp.route("/list/classrooms")
        def list_classrooms() -> list[str]:
            return _list_entity(Classroom)
