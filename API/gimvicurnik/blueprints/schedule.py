from __future__ import annotations

import typing

from .base import BaseHandler
from ..database import Class, LunchSchedule, Session

if typing.TYPE_CHECKING:
    import datetime
    from typing import Any
    from flask import Blueprint
    from ..config import Config


class ScheduleHandler(BaseHandler):
    name = "schedule"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        @bp.route("/schedule/date/<date:date>")
        def get_lunch_schedule(date: datetime.date) -> list[dict[str, Any]]:
            return [
                {
                    "class": model[1],
                    "date": model[0].date.strftime("%Y-%m-%d"),
                    "time": model[0].time.strftime("%H:%M"),
                    "location": model[0].location,
                    "notes": model[0].notes,
                }
                for model in (
                    Session.query(LunchSchedule, Class.name)
                    .join(Class)
                    .filter(LunchSchedule.date == date)
                    .order_by(LunchSchedule.time, LunchSchedule.class_)
                )
            ]

        @bp.route("/schedule/date/<date:date>/classes/<list:classes>")
        def get_lunch_schedule_for_classes(date: datetime.date, classes: list[str]) -> list[dict[str, Any]]:
            return [
                {
                    "class": model[1],
                    "date": model[0].date.strftime("%Y-%m-%d"),
                    "time": model[0].time.strftime("%H:%M"),
                    "location": model[0].location,
                    "notes": model[0].notes,
                }
                for model in (
                    Session.query(LunchSchedule, Class.name)
                    .join(Class)
                    .filter(LunchSchedule.date == date, Class.name.in_(classes))
                    .order_by(LunchSchedule.time, LunchSchedule.class_)
                )
            ]
