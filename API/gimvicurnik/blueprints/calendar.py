from __future__ import annotations

import logging
import typing
from datetime import date, datetime, timedelta
from hashlib import sha256

from flask import make_response, request
from icalendar import Calendar, Event, vDuration, vRecur  # type: ignore

from .base import BaseHandler
from ..database import Class, LunchSchedule, Session
from ..utils.sentry import start_span, with_span

if typing.TYPE_CHECKING:
    from typing import Any
    from collections.abc import Iterator
    from flask import Blueprint, Response
    from sqlalchemy.orm.query import RowReturningQuery
    from ..config import Config, ConfigLessonTime


def create_calendar(name: str, url: str) -> Calendar:
    calendar = Calendar()

    calendar.add("PRODID", "gimvicurnik")
    calendar.add("VERSION", "2.0")
    calendar.add("X-WR-TIMEZONE", "Europe/Ljubljana")
    calendar.add("X-WR-CALNAME", name)
    calendar.add("X-WR-CALDESC", name)
    calendar.add("NAME", name)
    calendar.add("URL", url)
    calendar.add("SOURCE", url)
    calendar.add("UID", sha256(url.encode("utf-8")).hexdigest())
    calendar.add("X-PUBLISHED-TTL", vDuration(timedelta(hours=1)))
    calendar.add("REFRESH-INTERVAL", vDuration(timedelta(hours=1)))

    return calendar


@with_span(op="generate")
def create_school_calendar(
    substitutions: Iterator[dict[str, Any]],
    lessons: Iterator[dict[str, Any]],
    times: list[ConfigLessonTime],
    name: str,
    url: str,
    include_timetable: bool = True,
    include_substitutions: bool = True,
) -> Response:
    """Create a school calendar from substitutions and timetable."""

    logger = logging.getLogger(__name__)
    calendar = create_calendar(name, url)

    today = datetime.now().date()
    year = today.year if today >= date(today.year, 9, 1) else today.year - 1

    weekdays = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]
    weektable: list[list[Event | None]] = [[None for _ in range(11)] for _ in range(6)]

    if include_timetable:
        for subject in lessons:
            with start_span(op="event") as span:
                span.set_tag("event.type", "timetable")
                span.set_tag("event.day", subject["day"])
                span.set_tag("event.time", subject["time"])
                span.set_data("event.source", subject)

                logger.debug(
                    "Preparing iCalendar event",
                    extra={"type": "timetable", "source": subject},
                )

                # Create event and add internal properties
                event = Event()
                event.add("DTSTAMP", datetime.now())
                event.add("CATEGORIES", ["Lesson", "Normal"])
                event.add("COLOR", "darkgreen")
                event.add(
                    "UID",
                    sha256(
                        (
                            str(subject["day"])
                            + str(subject["time"])
                            + str(subject["subject"])
                            + str(subject["class"])
                            + str(subject["classroom"])
                            + str(subject["teacher"])
                        ).encode("utf-8")
                    ).hexdigest(),
                )

                # Add basic lesson properties
                event.add("SUMMARY", subject["subject"])
                event.add("ATTENDEE", subject["class"])
                event.add("ORGANIZER", subject["teacher"])
                event.add("LOCATION", subject["classroom"])
                event.add("DURATION", timedelta(minutes=45))

                # Lesson "starts" on -08-31, so it can repeat properly
                start = datetime(year, 8, 31) + times[subject["time"]].start
                event.add("DTSTART", start)
                event.add("EXDATE", start)

                # Lesson repeats every week
                event.add(
                    "RRULE",
                    vRecur(
                        freq="WEEKLY",
                        byday=weekdays[subject["day"]],
                        until=datetime(year + 1, 6, 25),
                    ),
                )

                # Add lesson to the week table
                weektable[subject["day"]][subject["time"]] = event

    if include_substitutions:
        for subject in substitutions:
            with start_span(op="event") as span:
                span.set_tag("event.type", "substitution")
                span.set_tag("event.date", subject["date"])
                span.set_tag("event.day", subject["day"])
                span.set_tag("event.time", subject["time"])
                span.set_data("event.source", subject)

                logger.debug(
                    "Preparing iCalendar event",
                    extra={"type": "substitution", "source": subject},
                )

                # Create event and add internal properties
                event = Event()
                event.add("DTSTAMP", datetime.now())
                event.add("CATEGORIES", ["Lesson", "Substitution"])
                event.add("COLOR", "darkred")
                event.add(
                    "UID",
                    sha256(
                        (
                            str(subject["date"])
                            + str(subject["day"])
                            + str(subject["time"])
                            + str(subject["subject"])
                            + str(subject["class"])
                            + str(subject["classroom"])
                            + str(subject["teacher"])
                            + str(subject["original-classroom"])
                            + str(subject["original-teacher"])
                        ).encode("utf-8")
                    ).hexdigest(),
                )

                # Add basic substitution properties
                event.add("SUMMARY", subject["subject"])
                event.add("DESCRIPTION", subject["notes"] or "")
                event.add("ATTENDEE", subject["class"])
                event.add("ORGANIZER", subject["teacher"])
                event.add("LOCATION", subject["classroom"])

                # Add start and end dates
                date_ = datetime.strptime(subject["date"], "%Y-%m-%d")
                event.add("DTSTART", date_ + times[subject["time"]].start)
                event.add("DTEND", date_ + times[subject["time"]].end)

                # Exclude normal lesson at that time
                if weektable[date_.isoweekday()][subject["time"]]:
                    original: Event = weektable[date_.isoweekday()][subject["time"]]
                    original.add("EXDATE", event.get("DTSTART"))

                # Add substitution to the calendar
                calendar.add_component(event)

    # Add all lessons to the calendar
    for day in range(len(weektable)):
        for time in range(len(weektable[0])):
            if weektable[day][time]:
                calendar.add_component(weektable[day][time])

    # Convert to iCal and return response
    response = make_response(calendar.to_ical().decode("utf-8").replace("\\", ""))
    response.headers["Content-Disposition"] = "attachment; filename=calendar.ics"
    response.headers["Content-Type"] = "text/calendar; charset=utf-8"
    return response


@with_span(op="generate")
def create_schedule_calendar(
    query: RowReturningQuery[tuple[LunchSchedule, str]],
    name: str,
    url: str,
) -> Response:
    logger = logging.getLogger(__name__)
    calendar = create_calendar(name, url)

    for model, classname in query:
        with start_span(op="event") as span:
            span.set_tag("event.type", "lunch-schedule")
            span.set_tag("event.date", model.date)
            span.set_tag("event.time", model.time)
            span.set_data("event.source", model)

            # Skip schedules without time
            if not model.time:
                logger.debug(
                    "Skipping iCalendar event",
                    extra={"type": "lunch-schedule", "source": model},
                )

                continue

            logger.debug(
                "Preparing iCalendar event",
                extra={"type": "lunch-schedule", "source": model},
            )

            # Create event and add internal properties
            event = Event()
            event.add("DTSTAMP", datetime.now())
            event.add("CATEGORIES", ["Lunch"])
            event.add("COLOR", "darkblue")
            event.add(
                "UID",
                sha256(
                    (
                        str(model.date)
                        + str(model.time)
                        + str(classname)
                        + str(model.location)
                        + str(model.notes)
                    ).encode("utf-8")
                ).hexdigest(),
            )

            # Add lunch schedule properties
            start = datetime.combine(model.date, model.time)
            end = start + timedelta(minutes=15)
            event.add("SUMMARY", "Kosilo")
            event.add("DESCRIPTION", model.notes or "")
            event.add("LOCATION", model.location or "")
            event.add("ATTENDEE", classname)
            event.add("DTSTART", start)
            event.add("DTEND", end)

            # Add lunch schedule to the calendar
            calendar.add_component(event)

    # Convert to iCal and return response
    response = make_response(calendar.to_ical().decode("utf-8").replace("\\", ""))
    response.headers["Content-Disposition"] = "attachment; filename=calendar.ics"
    response.headers["Content-Type"] = "text/calendar; charset=utf-8"
    return response


class CalendarHandler(BaseHandler):
    name = "calendar"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        @bp.route("/calendar/combined/<list:classes>")
        def get_combined_calendar_for_classes(classes: list[str]) -> Response:
            return create_school_calendar(
                Class.get_substitutions(None, classes),
                Class.get_lessons(classes),
                config.lessonTimes,
                f"Koledar \u2013 {', '.join(classes)} \u2013 Gimnazija Vič",
                config.urls.api + request.path,
            )

        @bp.route("/calendar/timetable/<list:classes>")
        def get_timetable_calendar_for_classes(classes: list[str]) -> Response:
            return create_school_calendar(
                Class.get_substitutions(None, classes),
                Class.get_lessons(classes),
                config.lessonTimes,
                f"Urnik \u2013 {', '.join(classes)} \u2013 Gimnazija Vič",
                config.urls.api + request.path,
                include_substitutions=False,
            )

        @bp.route("/calendar/substitutions/<list:classes>")
        def get_substitutions_calendar_for_classes(classes: list[str]) -> Response:
            return create_school_calendar(
                Class.get_substitutions(None, classes),
                Class.get_lessons(classes),
                config.lessonTimes,
                f"Nadomeščanja \u2013 {', '.join(classes)} \u2013 Gimnazija Vič",
                config.urls.api + request.path,
                include_timetable=False,
            )

        @bp.route("/calendar/schedules/<list:classes>")
        def get_schedules_calendar_for_classes(classes: list[str]) -> Response:
            return create_schedule_calendar(
                Session.query(LunchSchedule, Class.name)
                .join(Class)
                .filter(Class.name.in_(classes))
                .order_by(LunchSchedule.time, LunchSchedule.class_),
                f"Razporedi kosila \u2013 {', '.join(classes)} \u2013 Gimnazija Vič",
                config.urls.api + request.path,
            )
