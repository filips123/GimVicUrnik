import datetime
import hashlib
import logging
import os
import re
import tempfile

import requests
from pdf2docx import extract_tables

from ..database import Class, Classroom, Document, LunchSchedule, Substitution, Teacher
from ..errors import ClassroomApiError, InvalidRecordError, InvalidTokenError, LunchScheduleError
from ..utils.database import get_or_create
from ..utils.sentry import with_span
from ..utils.url import normalize_url, tokenize_url


class EClassroomUpdater:
    def __init__(self, config, session):
        self.url = config["url"]
        self.token = config["token"]
        self.course = config["course"]
        self.pluginfile = config["pluginfile"]

        self.session = session
        self.logger = logging.getLogger(__name__)

    def update(self):
        for name, url, date in self._get_documents():
            if "www.dropbox.com" in url:
                self._store_substitutions(name, url.replace("dl=0", "dl=1"))
            elif "delitevKosila" in url:
                self._store_lunch_schedule(name, url)
            elif "okroznica" in url.lower() or "okrožnica" in url.lower():
                self._store_generic(name, url, date, "circular")
            else:
                self._store_generic(name, url, date, "other")

    def _get_external_urls(self):
        params = {
            "moodlewsrestformat": "json",
        }
        data = {
            "wstoken": self.token,
            "wsfunction": "mod_url_get_urls_by_courses",
        }

        try:
            response = requests.post(self.url, params=params, data=data)
            objects = response.json()

            response.raise_for_status()
        except (IOError, ValueError) as error:
            raise ClassroomApiError("Error while accessing e-classroom API") from error

        # Handle API errors
        if "errorcode" in objects:
            if objects["errorcode"] == "invalidtoken":
                raise InvalidTokenError(objects["message"])
            else:
                raise ClassroomApiError(objects["message"])

        # Yield every external URL name, URL and date
        for object in objects["urls"]:
            if object["course"] != self.course:
                continue

            yield object["name"], object["externalurl"], datetime.datetime.fromtimestamp(object["timemodified"])

    def _get_documents(self):
        params = {
            "moodlewsrestformat": "json",
        }
        data = {
            "courseid": self.course,
            "wstoken": self.token,
            "wsfunction": "core_course_get_contents",
        }

        try:
            response = requests.post(self.url, params=params, data=data)
            objects = response.json()

            response.raise_for_status()
        except (IOError, ValueError) as error:
            raise ClassroomApiError("Error while accessing e-classroom API") from error

        # Handle API errors
        if "errorcode" in objects:
            if objects["errorcode"] == "invalidtoken":
                raise InvalidTokenError(objects["message"])
            elif objects["errorcode"] == "invalidrecord":
                raise InvalidRecordError(objects["message"])
            else:
                raise ClassroomApiError(objects["message"])

        # Yield every document name, URL and date
        for object in objects:
            for module in object["modules"]:
                if "contents" not in module or len(module["contents"]) == 0:
                    continue

                yield (
                    module["name"],
                    normalize_url(module["contents"][0]["fileurl"], self.pluginfile),
                    datetime.datetime.fromtimestamp(module["contents"][0]["timecreated"]).date(),
                )

        # Yield external URLs
        yield from self._get_external_urls()

    @with_span(op="document", pass_span=True)
    def _store_generic(self, name, url, date, urltype, span):
        # Add or skip new generic document
        model, created = get_or_create(session=self.session, model=Document, date=date, type=urltype, url=url, description=name)

        span.description = model.url
        span.set_tag("document.url", model.url)
        span.set_tag("document.type", model.type)
        span.set_tag("document.date", model.date)
        span.set_tag("document.action", "created" if created else "skipped")

        if created:
            self.logger.info("Created a new %s document", urltype)
        else:
            self.logger.info("Skipped because the %s document is already stored", urltype)

        self.logger.debug("URL: %s", model.url)
        self.logger.debug("Type: %s", model.type)
        self.logger.debug("Created: %s", model.date)

    @with_span(op="document", pass_span=True)
    def _store_substitutions(self, name, url, span):
        response = requests.get(url)

        content = response.content
        hash = str(hashlib.sha256(content).hexdigest())

        span.description = url
        span.set_tag("document.url", url)
        span.set_tag("document.type", "substitutions")

        # Skip unchanged substitutions documents
        document = self.session.query(Document).filter(Document.type == "substitutions", Document.url == url).first()
        if hash == getattr(document, "hash", False):
            self.logger.info("Skipped because the substitutions document for %s is unchanged", document.date)
            self.logger.debug("URL: %s", document.url)
            self.logger.debug("Date: %s", document.date)
            self.logger.debug("Hash: %s", document.hash)

            span.set_tag("document.date", document.date)
            span.set_tag("document.hash", document.hash)
            span.set_tag("document.action", "skipped")

            return

        date = datetime.datetime.strptime(re.search(r"_obvestila_(.+).pdf", url, re.IGNORECASE).group(1), "%d._%m._%Y").date()
        day = date.isoweekday()

        # Save content to temporary file
        filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex() + ".pdf")
        file = open(filename, mode="w+b")
        file.write(content)
        file.close()

        # Extract all tables from PDF file
        tables = with_span(op="extract")(extract_tables)(filename)
        os.remove(filename)

        header_substitutions = ["ODSOTNI UČITELJ/ICA", "URA", "RAZRED", "UČILNICA", "NADOMEŠČA", "PREDMET", "OPOMBA"]
        header_lesson_change = ["RAZRED", "URA", "UČITELJ/ICA", "PREDMETA", "UČILNICA", "OPOMBA"]
        header_subject_change = ["RAZRED", "URA", "UČITELJ", "PREDMET", "UČILNICA", "OPOMBA"]
        header_classroom_change = ["RAZRED", "URA", "UČITELJ/ICA", "PREDMET", "IZ UČILNICE", "V UČILNICO", "OPOMBA"]
        header_more_teachers = ["URA", "UČITELJ", "RAZRED", "UČILNICA", "OPOMBA"]
        header_reservations = ["URA", "UČILNICA", "REZERVIRAL/A", "OPOMBA"]

        substitutions = []

        parser_type = None
        last_original_teacher = None

        # Parse tables into substitutions
        for table in tables:
            for row in table:
                row = [column.replace("\n", " ").strip() if column else None for column in row]

                # Get parser type
                if row == header_substitutions:
                    parser_type = "substitutions"
                    continue
                elif row == header_lesson_change:
                    parser_type = "lesson-change"
                    continue
                elif row == header_subject_change:
                    parser_type = "subject-change"
                    continue
                elif row == header_classroom_change:
                    parser_type = "classroom-change"
                    continue
                elif row == header_more_teachers:
                    parser_type = "more-teachers"
                    continue
                elif row == header_reservations:
                    parser_type = "reservations"
                    continue

                # Parse substitutions
                if parser_type == "substitutions":
                    if not any(row):
                        self.logger.error(
                            "Something is wrong with the substitutions file; the row should have at least one non-empty value",
                            extra={"row": row},
                        )
                        continue

                    time = row[1][:-1] if row[1] != "PU" else 0
                    subject = self._normalize_other_names(row[5])

                    # Get original teacher if it is specified
                    original_teacher = self._normalize_teacher_name(row[0]) if row[0] else last_original_teacher
                    last_original_teacher = original_teacher

                    original_classroom = self._normalize_other_names(row[3])
                    classroom = original_classroom

                    # Handle multiple classes
                    classes = row[2].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    # Get new teacher
                    teacher = self._normalize_teacher_name(row[4])

                    # fmt: off
                    for class_ in classes:
                        substitutions.append(
                            {
                                "date": date,
                                "day": day,
                                "time": time,
                                "subject": subject,
                                "original_teacher_id": get_or_create(self.session, model=Teacher, name=original_teacher)[0].id if original_teacher else None,
                                "original_classroom_id": get_or_create(self.session, model=Classroom, name=original_classroom)[0].id if original_classroom else None,
                                "class_id": get_or_create(self.session, model=Class, name=class_)[0].id,
                                "teacher_id": get_or_create(self.session, model=Teacher, name=teacher)[0].id if teacher else None,
                                "classroom_id": get_or_create(self.session, model=Classroom, name=classroom)[0].id if classroom else None,
                            }
                        )
                    # fmt: on

                elif parser_type == "lesson-change":
                    time = row[1][:-1] if row[1] != "PU" else 0
                    subject = self._normalize_other_names(row[3].split(" → ")[1])

                    original_teacher = self._normalize_teacher_name(row[2].split(" → ")[0])
                    original_classroom = self._normalize_other_names(row[4])

                    # Handle multiple classes
                    classes = row[0].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    teacher = self._normalize_teacher_name(row[2].split(" → ")[1])
                    classroom = original_classroom

                    # fmt: off
                    for class_ in classes:
                        substitutions.append(
                            {
                                "date": date,
                                "day": day,
                                "time": time,
                                "subject": subject,
                                "original_teacher_id": get_or_create(self.session, model=Teacher, name=original_teacher)[0].id if original_teacher else None,
                                "original_classroom_id": get_or_create(self.session, model=Classroom, name=original_classroom)[0].id if original_classroom else None,
                                "class_id": get_or_create(self.session, model=Class, name=class_)[0].id,
                                "teacher_id": get_or_create(self.session, model=Teacher, name=teacher)[0].id if teacher else None,
                                "classroom_id": get_or_create(self.session, model=Classroom, name=classroom)[0].id if classroom else None,
                            }
                        )
                    # fmt: on

                elif parser_type == "subject-change":
                    time = row[1][:-1] if row[1] != "PU" else 0
                    subject = self._normalize_other_names(row[3].split(" → ")[1])

                    original_teacher = self._normalize_teacher_name(row[2])
                    original_classroom = self._normalize_other_names(row[4])

                    # Handle multiple classes
                    classes = row[0].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    teacher = original_teacher
                    classroom = original_classroom

                    # fmt: off
                    for class_ in classes:
                        substitutions.append(
                            {
                                "date": date,
                                "day": day,
                                "time": time,
                                "subject": subject,
                                "original_teacher_id": get_or_create(self.session, model=Teacher, name=original_teacher)[0].id if original_teacher else None,
                                "original_classroom_id": get_or_create(self.session, model=Classroom, name=original_classroom)[0].id if original_classroom else None,
                                "class_id": get_or_create(self.session, model=Class, name=class_)[0].id,
                                "teacher_id": get_or_create(self.session, model=Teacher, name=teacher)[0].id if teacher else None,
                                "classroom_id": get_or_create(self.session, model=Classroom, name=classroom)[0].id if classroom else None,
                            }
                        )
                    # fmt: on

                elif parser_type == "classroom-change":
                    time = row[1][:-1] if row[1] != "PU" else 0
                    subject = self._normalize_other_names(row[3])

                    original_teacher = self._normalize_teacher_name(row[2])
                    original_classrooms = [self._normalize_other_names(name) for name in row[4].split(", ")]

                    # Handle multiple classes
                    classes = row[0].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    teacher = original_teacher
                    classroom = self._normalize_other_names(row[5])

                    # fmt: off
                    for class_ in classes:
                        for original_classroom in original_classrooms:
                            substitutions.append(
                                {
                                    "date": date,
                                    "day": day,
                                    "time": time,
                                    "subject": subject,
                                    "original_teacher_id": get_or_create(self.session, model=Teacher, name=original_teacher)[0].id if original_teacher else None,
                                    "original_classroom_id": get_or_create(self.session, model=Classroom, name=original_classroom)[0].id if original_classroom else None,
                                    "class_id": get_or_create(self.session, model=Class, name=class_)[0].id,
                                    "teacher_id": get_or_create(self.session, model=Teacher, name=teacher)[0].id if teacher else None,
                                    "classroom_id": get_or_create(self.session, model=Classroom, name=classroom)[0].id if classroom else None,
                                }
                            )
                    # fmt: on

        # Store substitutions in database
        substitutions = [dict(element) for element in {tuple(substitution.items()) for substitution in substitutions}]

        self.session.query(Substitution).filter(Substitution.date == date).delete()
        self.session.bulk_insert_mappings(Substitution, substitutions)

        # Update or create a document
        if not document:
            document = Document()
            created = True
        else:
            created = False

        document.date = date
        document.type = "substitutions"
        document.url = url
        document.description = name.split(",")[0]
        document.hash = hash

        self.session.add(document)

        span.set_tag("document.date", document.date)
        span.set_tag("document.hash", document.hash)
        span.set_tag("document.action", "created" if created else "updated")

        if created:
            self.logger.info("Created a new substitutions document for %s", document.date)
        else:
            self.logger.info("Updated the substitutions document for %s", document.date)

    @with_span(op="document", pass_span=True)
    def _store_lunch_schedule(self, name, url, span):
        response = requests.get(tokenize_url(url, self.pluginfile, self.token))

        content = response.content
        hash = str(hashlib.sha256(content).hexdigest())

        span.description = url
        span.set_tag("document.url", url)
        span.set_tag("document.type", "lunch-schedule")

        # Skip unchanged lunch schedule document documents
        document = self.session.query(Document).filter(Document.type == "lunch-schedule", Document.url == url).first()
        if hash == getattr(document, "hash", False):
            self.logger.info("Skipped because the lunch schedule document for %s is unchanged", document.date)
            self.logger.debug("URL: %s", document.url)
            self.logger.debug("Date: %s", document.date)
            self.logger.debug("Hash: %s", document.hash)

            span.set_tag("document.date", document.date)
            span.set_tag("document.hash", document.hash)
            span.set_tag("document.action", "skipped")

            return

        # Save content to temporary file
        filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex() + ".pdf")
        file = open(filename, mode="w+b")
        file.write(content)
        file.close()

        # Extract all tables from PDF file
        tables = with_span(op="extract")(extract_tables)(filename)
        os.remove(filename)

        # Daily lunch schedule format, used until October 2020
        # Example: delitevKosila-0-15-okt2020-CET-objava.pdf
        if re.search(r"\/delitevKosila-0-[0-9]+-[a-z0-9]+-[A-Z]{3}-(?i:objava)\.pdf$", url):
            date = self._get_daily_lunch_schedule_date(name, url)
            self._parse_daily_lunch_schedule(date, tables)

        # Weekly lunch schedule format, used in February 2021
        # Example: delitevKosila-15-19-feb2021.pdf
        elif re.search(r"\/delitevKosila-[1-9][0-9]+-[1-9][0-9]+-[a-z0-9]+(?:-popravek-[a-z0-9]+)?\.pdf$", url):
            date = self._get_weekly_lunch_schedule_date(name, url)
            self._parse_weekly_lunch_schedule(date, tables)

        # Daily lunch schedule format, used starting with March 2021
        # Example: delitevKosila-mar9-2021-TOR-objava-PDF-0.pdf
        # Example: delitevKosila-1sept2021-SRE-objava-PDF.pdf
        # Example: delitevKosila-1feb2022-objava-PDF.pdf
        elif re.search(r"\/delitevKosila-[a-z0-9]+(?:-[0-9]+)?(?:-[A-Z]{3})?-(?i:objava).*\.pdf$", url):
            date = self._get_daily_lunch_schedule_date(name, url)
            self._parse_daily_lunch_schedule(date, tables)

        # Unknown lunch schedule format
        else:
            raise LunchScheduleError("Unknown lunch schedule format: " + url.rsplit("/", 1)[-1])

        # Get lunch schedule for the same date if schedule was updated and URL has changed
        if not document:
            document = self.session.query(Document).filter(Document.type == "lunch-schedule", Document.date == date).first()

        # Update or create a document
        if not document:
            document = Document()
            created = True
        else:
            created = False

        document.date = date
        document.type = "lunch-schedule"
        document.url = url
        document.description = name.split(",")[0].split("-")[0].capitalize()
        document.hash = hash

        self.session.add(document)

        span.set_tag("document.date", document.date)
        span.set_tag("document.hash", document.hash)
        span.set_tag("document.action", "created" if created else "updated")

        if created:
            self.logger.info("Created a new lunch schedule document for %s", document.date)
        else:
            self.logger.info("Updated the lunch schedule document for %s", document.date)

    @staticmethod
    def _normalize_teacher_name(name):
        # Special case: Additional lesson
        if name == "Po urniku ni pouka":
            return None

        # Special case: Unknown teacher
        if name == "X" or name == "x" or name == "/" or name == "MANJKA":
            return None

        # Special case: Multiple Krapež teachers
        if "Krapež" in name:
            if "Alenka" in name:
                return "KrapežA"
            elif "Marjetka" in name:
                return "KrapežM"

        # Special case: Teachers with multiple surnames
        teachers = {
            "Crnoja": "Legan",
            "Erbežnik": "Mihelič",
            "Gresl": "Černe",
            "Jereb": "Batagelj",
            "Merhar": "Kariž",
            "Osole": "Pikl",
            "Stjepić": "Šajn",
            "Tehovnik": "Glaser",
            "Vahtar": "Rudolf",
            "Potočnik": "Vičar",
            "Završnik": "Ražen",
            "Zelič": "Ocvirk",
            "Žemva": "Strmčnik",
        }
        if name.split()[0] in teachers:
            return teachers[name.split()[0]]

        # Use only surname and replace ć with č
        return name.split()[0].replace("ć", "č")

    @staticmethod
    def _normalize_other_names(name):
        # Special case: Unknown entity
        if name == "X" or name == "x" or name == "/" or name == "MANJKA":
            return None

        return name

    @staticmethod
    def _get_daily_lunch_schedule_date(name, url):
        search = re.search(r"([0-9]+). ?([0-9]+). ?([0-9]+)", name.split(",")[-1].split("-")[-1].strip())
        return datetime.date(year=int(search.group(3)), month=int(search.group(2)), day=int(search.group(1)))

    @staticmethod
    def _get_weekly_lunch_schedule_date(name, url):
        month_to_number = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "maj": 5,
            "jun": 6,
            "jul": 7,
            "avg": 8,
            "sep": 9,
            "okt": 10,
            "nov": 11,
            "dec": 12,
        }

        search = re.search(r"\/delitevKosila-([1-9][0-9]+)-[0-9][1-9]+-([a-z]+)([1-9][0-9]+)(?:-popravek-[a-z0-9]+)?\.pdf$", url)
        return datetime.date(year=int(search.group(3)), month=month_to_number[search.group(2)], day=int(search.group(1)))

    def _parse_daily_lunch_schedule(self, date, tables):
        schedule = []

        last_hour = None
        last_notes = None

        for table in tables:
            # Skip instructions
            if not table[0][0] or "Dijaki prihajate v jedilnico" in table[0][0]:
                continue

            for index, row in enumerate(table):
                # Skip header
                if row[0] and "ura" in row[0]:
                    continue

                # Skip empty rows
                if len(row) != 5 or not row[0]:
                    continue

                # Handle multiple times in the same cell
                times = row[0].split("\n", 1)
                if len(times) == 2:
                    row[0] = times[0]
                    table[index + 1][0] = times[1]

                # Handle incorrectly connected cells
                if row[1] is None and len(row[0].split(" ", 1)) == 2:
                    row[0], row[1] = row[0].split(" ", 1)

                # Handle different time formats
                row[0] = row[0].strip().replace(".", ":")

                is_time_valid = row[0] and row[0].strip() != "do"
                time = datetime.datetime.strptime(row[0], "%H:%M").time() if is_time_valid else last_hour
                last_hour = time

                notes = row[1].strip() if row[0] else last_notes
                notes = notes if notes else None
                last_notes = notes

                classes = row[2].replace("(", "").replace(")", "").split(",")
                location = row[4].strip()

                for class_ in classes:
                    schedule.append(
                        {
                            "class_id": get_or_create(self.session, model=Class, name=class_.strip())[0].id,
                            "date": date,
                            "time": time,
                            "location": location,
                            "notes": notes,
                        }
                    )

        # Store schedule in database
        self.session.query(LunchSchedule).filter(LunchSchedule.date == date).delete()
        self.session.bulk_insert_mappings(LunchSchedule, schedule)

    def _parse_weekly_lunch_schedule(self, date, tables):
        schedule = []

        for table in tables:
            # Skip instructions
            if not table[0][0] or "V jedilnico prihajate z maskami" in table[0][0] or "JEDILNICA 1" in table[0][0]:
                continue

            for row in table:
                # Skip header
                if row[0] and "ura" in row[0]:
                    continue

                # Split if multiple cells are merged with newline
                if len(row) != 3:
                    row = [a for b in row for a in b.split("\n")]

                time = datetime.datetime.strptime(row[0].strip(), "%H:%M").time()
                classes = row[1].replace("(", "").replace(")", "").split(",")
                location = row[2].strip()

                for class_ in classes:
                    schedule.append(
                        {
                            "class_id": get_or_create(self.session, model=Class, name=class_.strip())[0].id,
                            "date": date,
                            "time": time,
                            "location": location,
                        }
                    )

            date += datetime.timedelta(days=1)

        # Store schedule in database
        self.session.query(LunchSchedule).filter(LunchSchedule.date == date).delete()
        self.session.bulk_insert_mappings(LunchSchedule, schedule)
