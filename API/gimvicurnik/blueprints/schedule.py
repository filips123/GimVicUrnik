from __future__ import annotations

import typing

from .base import BaseHandler
from ..database import Class, LunchSchedule, Session
from ..utils.dates import get_weekdays

if typing.TYPE_CHECKING:
    import datetime
    from typing import Any
    from flask import Blueprint
    from ..config import Config


class ScheduleHandler(BaseHandler):
    name = "schedule"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        def _serialize_schedule(schedule: LunchSchedule, class_: str) -> dict[str, Any]:
            return {
                "class": class_,
                "date": schedule.date.isoformat(),
                "time": schedule.time.isoformat("minutes") if schedule.time else None,
                "location": schedule.location,
                "notes": schedule.notes,
            }

        def _fetch_schedules_for_date(
            date: datetime.date,
            classes: list[str] | None = None,
        ) -> list[dict[str, Any]]:
            """Fetch lunch schedules for a specific date."""

            query = (
                Session.query(LunchSchedule, Class.name)
                .join(Class)
                .filter(LunchSchedule.date == date)
                .order_by(LunchSchedule.time, LunchSchedule.class_)
            )

            if classes:
                query = query.filter(Class.name.in_(classes))

            return [_serialize_schedule(model[0], model[1]) for model in query]

        def _fetch_schedules_for_week(
            weekdays: list[datetime.date],
            classes: list[str] | None = None,
        ) -> dict[datetime.date, list[dict[str, Any]]]:
            """Fetch lunch schedules for a specific week."""

            query = (
                Session.query(LunchSchedule, Class.name)
                .join(Class)
                .filter(LunchSchedule.date.in_(weekdays))
                .order_by(LunchSchedule.time, LunchSchedule.class_)
            )

            if classes:
                query = query.filter(Class.name.in_(classes))

            schedules: dict[datetime.date, list[dict[str, Any]]] = {day: [] for day in weekdays}

            for schedule, class_ in query.all():
                schedules[schedule.date].append(_serialize_schedule(schedule, class_))

            return schedules

        @bp.route("/schedule/date/<date:date>")
        def get_date_schedule(date: datetime.date) -> list[dict[str, Any]]:
            return _fetch_schedules_for_date(date)

        @bp.route("/schedule/date/<date:date>/classes/<list:classes>")
        def get_date_schedule_for_classes(date: datetime.date, classes: list[str]) -> list[dict[str, Any]]:
            return _fetch_schedules_for_date(date, classes)

        @bp.route("/schedule/week/<date:date>")
        def get_week_schedule(date: datetime.date) -> list[list[dict[str, Any]]]:
            weekdays = get_weekdays(date)
            schedules = _fetch_schedules_for_week(weekdays)
            return list(schedules.values())

        @bp.route("/schedule/week/<date:date>/classes/<list:classes>")
        def get_week_schedule_for_classes(
            date: datetime.date,
            classes: list[str],
        ) -> list[list[dict[str, Any]]]:
            weekdays = get_weekdays(date)
            schedules = _fetch_schedules_for_week(weekdays, classes)
            return list(schedules.values())
