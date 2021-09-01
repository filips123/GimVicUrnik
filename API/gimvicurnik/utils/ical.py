import logging
from datetime import datetime, timedelta, date

from flask import make_response
from icalendar import Calendar, Event, vDuration, vText, vDatetime
from hashlib import sha256

from .sentry import with_span, start_span


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def datecount(start_date, i):
    for n in range(i):
        yield start_date + timedelta(n)


@with_span(op="generate")
def create_school_calendar(details, timetables, hours, name, timetable=True, substitutions=True):
    logger = logging.getLogger(__name__)

    calendar = Calendar()
    calendar.add("prodid", "gimvicurnik")
    calendar.add("version", "2.0")
    calendar.add("X-WR-TIMEZONE", "Europe/Ljubljana")
    calendar.add("X-WR-CALNAME", name)
    calendar.add("X-WR-CALDESC", name)
    calendar.add("NAME", name)
    calendar.add("X-PUBLISHED-TTL", vDuration(timedelta(hours=1)))
    calendar.add("REFRESH-INTERVAL", vDuration(timedelta(hours=1)))

    year = datetime.now().year if datetime.now().date() > date(datetime.now().year, 9, 1) else datetime.now().year - 1

    weekdays = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]
    weektable = [[None for i in range(10)] for j in range(6)]

    if timetable:
        for subject in timetables:
            with start_span(op="event") as span:
                span.set_tag("event.type", "timetable")
                span.set_tag("event.day", subject["day"])
                span.set_tag("event.time", subject["time"])
                span.set_data("event.source", subject)

                logger.info("Preparing iCalendar event", extra={"type": "timetable", "source": subject})
                event = Event()

                event.add("dtstamp", datetime.now())
                event.add("CATEGORIES", vText("NORMAL"))
                event.add("COLOR", vText("green"))
                event.add(
                    "UID",
                    sha256(
                        (
                            str(subject["day"])
                            + str(subject["time"])
                            + str(subject["subject"])
                            + str(subject["class"])
                            + str(subject["teacher"])
                        ).encode()
                    ).hexdigest(),
                )

                start = datetime(year, 8, 31) + hours[subject["time"]]["hour"]["start"]
                event.add("dtstart", start)
                event["EXDATE"] = vDatetime(start).to_ical().decode("utf-8")
                event["DURATION"] = "PT45M"
                event["RRULE"] = (
                    "FREQ=WEEKLY;BYDAY="
                    + weekdays[subject["day"]]
                    + ";UNTIL="
                    + vDatetime(datetime(year + 1, 6, 25)).to_ical().decode("utf-8")
                )

                event.add("summary", subject["subject"])
                event["organizer"] = vText(subject["teacher"])
                event["location"] = vText(subject["classroom"])

                weektable[subject["day"]][subject["time"]] = event

    if substitutions:
        for subject in details:
            with start_span(op="event") as span:
                span.set_tag("event.type", "substitution")
                span.set_tag("event.date", subject["date"])
                span.set_tag("event.day", subject["day"])
                span.set_tag("event.time", subject["time"])
                span.set_data("event.source", subject)

                logger.info("Preparing iCalendar event", extra={"type": "substitution", "source": subject})

                event = Event()
                event.add("dtstamp", datetime.now())
                event.add("CATEGORIES", vText("SUBSTITUTION"))
                event.add("COLOR", vText("darkred"))
                event.add(
                    "UID",
                    sha256(
                        (
                            str(subject["date"])
                            + str(subject["day"])
                            + str(subject["time"])
                            + str(subject["subject"])
                            + str(subject["class"])
                            + str(subject["teacher"])
                        ).encode()
                    ).hexdigest(),
                )

                date_ = datetime.strptime(subject["date"], "%Y-%m-%d")
                event.add("dtstart", date_ + hours[subject["time"]]["hour"]["start"])
                event.add("dtend", date_ + hours[subject["time"]]["hour"]["end"])

                event.add("summary", subject["subject"])
                event["organizer"] = vText(subject["teacher"])
                event["location"] = vText(subject["classroom"])

                if weektable[datetime.strptime(subject["date"], "%Y-%m-%d").isoweekday()][subject["time"]]:
                    original = weektable[datetime.strptime(subject["date"], "%Y-%m-%d").isoweekday()][subject["time"]]
                    original["EXDATE"] += "," + event.get("dtstart").to_ical().decode("utf-8")

                calendar.add_component(event)

    for i in range(len(weektable)):
        for j in range(len(weektable[0])):
            if weektable[i][j]:
                calendar.add_component(weektable[i][j])

    response = make_response(calendar.to_ical().decode("utf-8").replace("\\", ""))
    response.headers["Content-Disposition"] = "attachment; filename=calendar.ics"
    response.headers["Content-Type"] = "text/calendar; charset=utf-8"
    return response


@with_span(op="generate")
def create_schedule_calendar(query, name):
    logger = logging.getLogger(__name__)

    calendar = Calendar()
    calendar.add("prodid", "gimvicurnik")
    calendar.add("version", "2.0")
    calendar.add("X-WR-TIMEZONE", "Europe/Ljubljana")
    calendar.add("X-WR-CALNAME", name)
    calendar.add("X-WR-CALDESC", name)
    calendar.add("NAME", name)
    calendar.add("X-PUBLISHED-TTL", vDuration(timedelta(hours=12)))
    calendar.add("REFRESH-INTERVAL", vDuration(timedelta(hours=12)))

    for model in query:
        with start_span(op="event") as span:
            span.set_tag("event.type", "lunch-schedule")
            span.set_tag("event.date", model.date)
            span.set_tag("event.time", model.time)
            span.set_data("event.source", model)

            logger.info("Preparing iCalendar event", extra={"type": "lunch-schedule", "source": model})

            event = Event()
            event.add("dtstamp", datetime.now())
            event.add("CATEGORIES", vText("LUNCH"))
            event.add("COLOR", vText("darkblue"))
            event.add(
                "UID",
                sha256((str(model.date) + str(model.time) + str(model.class_.name) + str(model.location)).encode()).hexdigest(),
            )

            event.add("summary", "Kosilo")
            event.add("description", model.notes or "")
            event.add("location", vText(model.location))
            event.add("dtstart", datetime.combine(model.date, model.time))
            event.add("dtend", datetime.combine(model.date, model.time) + timedelta(minutes=15))

            calendar.add_component(event)

    response = make_response(calendar.to_ical().decode("utf-8").replace("\\", ""))
    response.headers["Content-Disposition"] = "attachment; filename=calendar.ics"
    response.headers["Content-Type"] = "text/calendar; charset=utf-8"
    return response
