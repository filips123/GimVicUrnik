from datetime import datetime, timedelta, date
from icalendar import Calendar, Event, vText, vDatetime
from hashlib import sha256


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def datecount(start_date, i):
    for n in range(i):
        yield start_date + timedelta(n)


def createCalendar(details, timetables, hours, timetable=True, substitutions=True):
    calendar = Calendar()
    calendar.add("prodid", "gimvicurnik")
    calendar.add("version", "2.0")
    weekdays = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]
    weektable = [[None for i in range(8)] for j in range(6)]
    if timetable:
        for subject in timetables:
            event = Event()
            event.add("dtstamp", datetime.now())
            year = datetime.now().year if datetime.now().date() > date(datetime.now().year, 9, 1) else datetime.now().year - 1
            event.add("dtstart", datetime(year, 9, 1) + hours[subject["time"]]["hour"]["start"])
            event.add(
                "UID",
                sha256(
                    (
                        str(subject["day"]) + str(subject["time"]) + subject["subject"] + subject["class"] + subject["teacher"]
                    ).encode()
                ).hexdigest(),
            )
            event["DURATION"] = "PT45M"
            event["RRULE"] = (
                "FREQ=WEEKLY;BYDAY="
                + weekdays[subject["day"]]
                + ";UNTIL="
                + vDatetime(datetime(year + 1, 6, 25)).to_ical().decode("utf-8")
            )
            event["EXDATE"] = vDatetime(datetime(year, 9, 1)).to_ical().decode("utf-8")
            event.add("summary", subject["subject"])
            event["organizer"] = vText(subject["teacher"])
            event["location"] = vText(subject["classroom"])
            weektable[subject["day"]][subject["time"]] = event
    if substitutions:
        for evedet in details:
            event = Event()
            event.add("dtstamp", datetime.now())
            print("here")
            event.add(
                "UID", sha256((evedet["date"] + evedet["subject"] + evedet["class"] + evedet["teacher"]).encode()).hexdigest()
            )
            print(evedet["date"], hours[evedet["time"]]["hour"]["start"])
            event.add("dtstart", (datetime.strptime(evedet["date"], "%Y%m%d") + hours[evedet["time"]]["hour"]["start"]))
            event.add("dtend", (datetime.strptime(evedet["date"], "%Y%m%d") + hours[evedet["time"]]["hour"]["end"]))
            event.add("summary", evedet["subject"])
            event["organizer"] = vText(evedet["teacher"])
            if weektable[datetime.strptime(evedet["date"], "%Y%m%d").isoweekday()][evedet["time"]]:
                datetime.strptime(evedet["date"], "%Y%m%d")
                weektable[datetime.strptime(evedet["date"], "%Y%m%d").isoweekday()][evedet["time"]]["EXDATE"] += "," + vDatetime(
                    (datetime.strptime(evedet["date"], "%Y%m%d"))
                ).to_ical().decode("utf-8")
            calendar.add_component(event)
    for i in range(len(weektable)):
        for j in range(len(weektable[0])):
            if weektable[i][j]:
                calendar.add_component(weektable[i][j])
    print(calendar.to_ical())
    return calendar.to_ical().decode("utf-8").replace("\\", "")
