from __future__ import annotations

import enum
import logging
import os
import re
import tempfile
import typing
from datetime import date, datetime, timezone

import requests
from pdf2docx import extract_tables  # type: ignore

from .base import BaseMultiUpdater, DocumentInfo
from ..database import Class, Classroom, DocumentType, LunchSchedule, Substitution, Teacher
from ..errors import ClassroomApiError, InvalidRecordError, InvalidTokenError
from ..utils.database import get_or_create
from ..utils.sentry import with_span

if typing.TYPE_CHECKING:
    from typing import Any, Dict, Iterator, List, Optional
    from sqlalchemy.orm import Session
    from sentry_sdk.tracing import Span
    from ..config import ConfigSourcesEClassroom
    from typing import Iterator
    from sqlalchemy.orm import Session
    from sentry_sdk.tracing import Span


class ParserType(enum.Enum):
    SUBSTITUTUONS = "substitutions"
    LESSON_CHANGE = "lesson-change"
    SUBJECT_CHANGE = "subject-change"
    CLASSROOM_CHANGE = "classroom-change"
    MORE_TEACHERS = "more-teachers"
    RESERVATIONS = "reservations"


class EClassroomUpdater(BaseMultiUpdater):
    source = "eclassroom"
    error = ClassroomApiError

    def __init__(self, config: ConfigSourcesEClassroom, session: Session) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.session = session

    def get_documents(self) -> Iterator[DocumentInfo]:
        """Get all documents from the e-classroom."""

        yield from self._get_internal_urls()
        yield from self._get_external_urls()

    def _get_internal_urls(self) -> Iterator[DocumentInfo]:
        params = {
            "moodlewsrestformat": "json",
        }
        data = {
            "courseid": self.config.course,
            "wstoken": self.config.token,
            "wsfunction": "core_course_get_contents",
        }

        try:
            response = requests.post(self.config.webserviceUrl, params=params, data=data)
            contents = response.json()

            response.raise_for_status()
        except (IOError, ValueError) as error:
            raise ClassroomApiError("Error while accessing e-classroom API") from error

        # Handle API errors
        if "errorcode" in contents:
            if contents["errorcode"] == "invalidtoken":
                raise InvalidTokenError(contents["message"])
            elif contents["errorcode"] == "invalidrecord":
                raise InvalidRecordError(contents["message"])
            else:
                raise ClassroomApiError(contents["message"])

        # Yield every document name, URL and date
        for content in contents:
            for module in content["modules"]:
                if "contents" not in module or len(module["contents"]) == 0:
                    continue

                yield DocumentInfo(
                    url=self.normalize_url(module["contents"][0]["fileurl"]),
                    type=self._get_document_type(module["contents"][0]["fileurl"]),
                    title=module["name"],
                    created=datetime.fromtimestamp(module["contents"][0]["timecreated"], tz=timezone.utc),
                    modified=datetime.fromtimestamp(module["contents"][0]["timemodified"], tz=timezone.utc),
                )

    def _get_external_urls(self) -> Iterator[DocumentInfo]:
        params = {
            "moodlewsrestformat": "json",
        }
        data = {
            "wstoken": self.config.token,
            "wsfunction": "mod_url_get_urls_by_courses",
        }

        try:
            response = requests.post(self.config.webserviceUrl, params=params, data=data)
            contents = response.json()

            response.raise_for_status()
        except (IOError, ValueError) as error:
            raise ClassroomApiError("Error while accessing e-classroom API") from error

        # Handle API errors
        if "errorcode" in contents:
            if contents["errorcode"] == "invalidtoken":
                raise InvalidTokenError(contents["message"])
            else:
                raise ClassroomApiError(contents["message"])

        # Yield every external URL name, URL and date
        for content in contents["urls"]:
            if content["course"] != self.config.course:
                continue

            yield DocumentInfo(
                url=self.normalize_url(content["externalurl"]),
                type=self._get_document_type(content["externalurl"]),
                title=content["name"],
                created=datetime.fromtimestamp(content["timecreated"], tz=timezone.utc),
                modified=datetime.fromtimestamp(content["timemodified"], tz=timezone.utc),
            )

    @staticmethod
    def _get_document_type(url: str) -> DocumentType:
        """Get a document type based on its URL."""

        if "www.dropbox.com" in url:
            return DocumentType.SUBSTITUTIONS
        elif "delitevKosila" in url:
            return DocumentType.LUNCH_SCHEDULE
        elif "okroznica" in url.lower() or "okrožnica" in url.lower():
            return DocumentType.CIRCULAR
        else:
            return DocumentType.OTHER

    def normalize_url(self, url: str) -> str:
        """Convert an e-classroom webservice URL to a normal URL."""

        return (
            url.replace(self.config.pluginFileWebserviceUrl, self.config.pluginFileNormalUrl)
            .replace("?forcedownload=1", "")
            .replace("?dl=0", "?raw=1")
        )

    def tokenize_url(self, url: str) -> str:
        """Convert a normal e-classroom URL to a webservice URL and add the token."""

        if self.config.pluginFileNormalUrl in url:
            return (
                url.replace(self.config.pluginFileNormalUrl, self.config.pluginFileWebserviceUrl)
                + "?token="
                + self.config.token
            )

        return url

    def get_document_title(self, document: DocumentInfo) -> str:
        """Return the normalized document title."""

        assert document.title

        if document.type == DocumentType.SUBSTITUTIONS:
            return document.title.split(",")[0]

        if document.type == DocumentType.LUNCH_SCHEDULE:
            return document.title.split(",")[0].split("-")[0].capitalize()

        return document.title

    @typing.no_type_check  # Ignored because if regex fails, we cannot do anything
    def get_document_effective(self, document: DocumentInfo) -> date:
        """Return the document effective date in a local timezone."""

        if document.type == DocumentType.SUBSTITUTIONS:
            effective = re.search(r"_obvestila_(.+).pdf", document.url, re.IGNORECASE).group(1)
            return datetime.strptime(effective, "%d._%m._%Y").date()

        if document.type == DocumentType.LUNCH_SCHEDULE:
            title = document.title.split(",")[-1].split("-")[-1].strip()
            search = re.search(r"(\d+). ?(\d+). ?(\d+)", title)
            return date(year=int(search.group(3)), month=int(search.group(2)), day=int(search.group(1)))

        # This cannot happen because only substitutions and schedules are provided
        raise KeyError("Unknown parsable document type from the e-classroom")

    def document_needs_parsing(self, document: DocumentInfo) -> bool:
        """Return whether the document needs parsing."""

        if document.type == DocumentType.SUBSTITUTIONS or document.type == DocumentType.LUNCH_SCHEDULE:
            return True

        return False

    @with_span(op="parse", pass_span=True)
    def parse_document(self, document: DocumentInfo, content: bytes, effective: date, span: Span) -> None:  # type: ignore[override]
        """Parse the document and store extracted data."""

        # Set basic Sentry span info
        span.set_tag("document.format", "pdf")
        span.set_tag("document.type", document.type.value)

        # Save the content to a temporary file
        filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex() + ".pdf")
        file = open(filename, mode="w+b")
        file.write(content)
        file.close()

        # Extract tables from the PDF file
        tables = with_span(op="extract")(extract_tables)(filename)
        os.remove(filename)

        if document.type == DocumentType.SUBSTITUTIONS:
            self._parse_substitutions(tables, effective, document.url)
        elif document.type == DocumentType.LUNCH_SCHEDULE:
            self._parse_lunch_schedule(tables, effective)
        else:
            # This cannot happen because only menus are provided by the API
            raise KeyError("Unknown parsable document type from the e-classroom")

    @staticmethod
    def _normalize_teacher_name(name: str) -> Optional[str]:
        """Normalize the teacher name."""

        # Special case: Additional lesson
        if name == "Po urniku ni pouka":
            return None

        # Special case: Unknown teacher
        if not name or name == "X" or name == "x" or name == "/" or name == "MANJKA":
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
    def _normalize_other_names(name: str) -> Optional[str]:
        """Normalize other types of names."""

        # Special case: Unknown entity
        if name == "X" or name == "x" or name == "/" or name == "MANJKA":
            return None

        return name

    def _format_substitution(
        self,
        effective: date,
        day: int,
        time: int,
        subject: Optional[str],
        original_teacher: Optional[str],
        original_classroom: Optional[str],
        class_: str,
        teacher: Optional[str],
        classroom: Optional[str],
    ) -> Dict[str, Any]:
        """Format the substitution into a dict that can be stored to a database."""

        # fmt: off
        return {
            "date": effective,
            "day": day,
            "time": time,
            "subject": subject,
            "original_teacher_id": get_or_create(self.session, model=Teacher, name=original_teacher)[0].id if original_teacher else None,
            "original_classroom_id": get_or_create(self.session, model=Classroom, name=original_classroom)[0].id if original_classroom else None,
            "class_id": get_or_create(self.session, model=Class, name=class_)[0].id,
            "teacher_id": get_or_create(self.session, model=Teacher, name=teacher)[0].id if teacher else None,
            "classroom_id": get_or_create(self.session, model=Classroom, name=classroom)[0].id if classroom else None,
        }
        # fmt: on

    def _parse_substitutions(self, tables: List[Any], effective: date, url: str) -> None:
        """Parse the substitutions document."""

        # fmt: off
        header_substitutions = ["ODSOTNI UČITELJ/ICA", "URA", "RAZRED", "UČILNICA", "NADOMEŠČA", "PREDMET", "OPOMBA"]
        header_lesson_change = ["RAZRED", "URA", "UČITELJ/ICA", "PREDMETA", "UČILNICA", "OPOMBA"]
        header_subject_change = ["RAZRED", "URA", "UČITELJ", "PREDMET", "UČILNICA", "OPOMBA"]
        header_classroom_change = ["RAZRED", "URA", "UČITELJ/ICA", "PREDMET", "IZ UČILNICE", "V UČILNICO", "OPOMBA"]
        header_more_teachers = ["URA", "UČITELJ", "RAZRED", "UČILNICA", "OPOMBA"]
        header_reservations = ["URA", "UČILNICA", "REZERVIRAL/A", "OPOMBA"]
        # fmt: on

        day = effective.isoweekday()
        substitutions = []

        parser_type = None
        last_original_teacher = None

        # Parse tables into substitutions
        for table in tables:
            for row in table:
                row = [column.replace("\n", " ").strip() if column else None for column in row]

                # Get parser type
                if row == header_substitutions:
                    parser_type = ParserType.SUBSTITUTUONS
                    continue
                elif row == header_lesson_change:
                    parser_type = ParserType.LESSON_CHANGE
                    continue
                elif row == header_subject_change:
                    parser_type = ParserType.SUBJECT_CHANGE
                    continue
                elif row == header_classroom_change:
                    parser_type = ParserType.CLASSROOM_CHANGE
                    continue
                elif row == header_more_teachers:
                    parser_type = ParserType.MORE_TEACHERS
                    continue
                elif row == header_reservations:
                    parser_type = ParserType.RESERVATIONS
                    continue

                # Parse substitutions
                if parser_type == ParserType.SUBSTITUTUONS:
                    if not any(row):
                        self.logger.error(
                            "Something is wrong with the substitutions file; "
                            "the row should have at least one non-empty value",
                            extra={"row": row, "url": url},
                            stack_info=True,
                        )
                        continue

                    time = row[1][:-1] if row[1] != "PU" else 0
                    subject = self._normalize_other_names(row[5])

                    # Get original teacher if it is specified
                    # fmt: off
                    original_teacher = self._normalize_teacher_name(row[0]) if row[0] else last_original_teacher
                    last_original_teacher = original_teacher
                    # fmt: on

                    # Get classroom (which stays the same)
                    original_classroom = self._normalize_other_names(row[3])
                    classroom = original_classroom

                    # Handle multiple classes
                    classes = row[2].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    # Get new teacher
                    teacher = self._normalize_teacher_name(row[4])

                    for class_ in classes:
                        substitutions.append(
                            self._format_substitution(
                                effective,
                                day,
                                time,
                                subject,
                                original_teacher,
                                original_classroom,
                                class_,
                                teacher,
                                classroom,
                            )
                        )

                elif parser_type == ParserType.LESSON_CHANGE:
                    time = row[1][:-1] if row[1] != "PU" else 0
                    subject = self._normalize_other_names(row[3].split(" → ")[1])

                    original_teacher = self._normalize_teacher_name(row[2].split(" → ")[0])
                    original_classroom = self._normalize_other_names(row[4])

                    # Handle multiple classes
                    classes = row[0].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    teacher = self._normalize_teacher_name(row[2].split(" → ")[1])
                    classroom = original_classroom

                    for class_ in classes:
                        substitutions.append(
                            self._format_substitution(
                                effective,
                                day,
                                time,
                                subject,
                                original_teacher,
                                original_classroom,
                                class_,
                                teacher,
                                classroom,
                            )
                        )

                elif parser_type == ParserType.SUBJECT_CHANGE:
                    time = row[1][:-1] if row[1] != "PU" else 0
                    subject = self._normalize_other_names(row[3].split(" → ")[1])

                    original_teacher = self._normalize_teacher_name(row[2])
                    original_classroom = self._normalize_other_names(row[4])

                    # Handle multiple classes
                    classes = row[0].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    teacher = original_teacher
                    classroom = original_classroom

                    for class_ in classes:
                        substitutions.append(
                            self._format_substitution(
                                effective,
                                day,
                                time,
                                subject,
                                original_teacher,
                                original_classroom,
                                class_,
                                teacher,
                                classroom,
                            )
                        )

                elif parser_type == ParserType.CLASSROOM_CHANGE:
                    time = row[1][:-1] if row[1] != "PU" else 0
                    subject = self._normalize_other_names(row[3])

                    original_teacher = self._normalize_teacher_name(row[2])
                    original_classrooms = [self._normalize_other_names(name) for name in row[4].split(", ")]

                    # Handle multiple classes
                    classes = row[0].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    teacher = original_teacher
                    classroom = self._normalize_other_names(row[5])

                    for class_ in classes:
                        for original_classroom in original_classrooms:
                            substitutions.append(
                                self._format_substitution(
                                    effective,
                                    day,
                                    time,
                                    subject,
                                    original_teacher,
                                    original_classroom,
                                    class_,
                                    teacher,
                                    classroom,
                                )
                            )

        # Deduplicate substitutions
        substitutions = [dict(subs2) for subs2 in {tuple(subs1.items()) for subs1 in substitutions}]

        # Store substitutions to a database
        self.session.query(Substitution).filter(Substitution.date == effective).delete()
        self.session.bulk_insert_mappings(Substitution, substitutions)

    def _parse_lunch_schedule(self, tables: List[Any], effective: date) -> None:
        """Parse the lunch schedule document."""

        schedule = []

        last_hour = None
        last_notes = None

        for table in tables:
            # Skip instructions
            if not table[0][0] or "Dijaki prihajate v jedilnico" in table[0][0]:
                continue

            for index, row in enumerate(table):
                # Handle incorrectly connected cells
                if row[0] and "\n" in row[0] and len(row) == 4:
                    time, notes = row[0].split("\n", 1)
                    row[0] = time
                    row.insert(1, notes)

                # Skip the header
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

                # Get the new time if it is specified
                is_time_valid = row[0] and row[0].strip() != "do"
                time = datetime.strptime(row[0], "%H:%M").time() if is_time_valid else last_hour
                last_hour = time

                # Get the new notes if they are specified
                notes = row[1].strip() if row[0] else last_notes
                notes = notes or None
                last_notes = notes

                # Get classes and location if they are specified
                classes = row[2].replace("(", "").replace(")", "").split(",") if row[2] else None
                location = row[4].strip() if row[4] else None

                for class_ in classes:
                    schedule.append(
                        {
                            "class_id": get_or_create(self.session, model=Class, name=class_.strip())[0].id,
                            "date": effective,
                            "time": time,
                            "location": location,
                            "notes": notes,
                        }
                    )

        # Store schedule to a database
        self.session.query(LunchSchedule).filter(LunchSchedule.date == effective).delete()
        self.session.bulk_insert_mappings(LunchSchedule, schedule)
