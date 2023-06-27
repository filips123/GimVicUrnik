from __future__ import annotations

import enum
import io
import logging
import os
import re
import tempfile
import typing
from datetime import date, datetime, timezone
from itertools import product

from mammoth import convert_to_html  # type: ignore
from sqlalchemy import insert

from .base import BaseMultiUpdater, DocumentInfo
from ..database import Class, Classroom, DocumentType, LunchSchedule, Substitution, Teacher
from ..errors import ClassroomApiError, InvalidRecordError, InvalidTokenError
from ..utils.database import get_or_create
from ..utils.pdf import extract_tables
from ..utils.sentry import with_span

if typing.TYPE_CHECKING:
    from typing import Any, Iterator
    from mammoth.documents import Image  # type: ignore
    from sqlalchemy.orm import Session
    from sentry_sdk.tracing import Span
    from ..config import ConfigSourcesEClassroom
    from ..utils.pdf import Tables


class ParserType(enum.Enum):
    SUBSTITUTUONS = "substitutions"
    LESSON_CHANGE = "lesson-change"
    SUBJECT_CHANGE = "subject-change"
    CLASSROOM_CHANGE = "classroom-change"
    MORE_TEACHERS = "more-teachers"
    RESERVATIONS = "reservations"
    UNKNOWN = "unknown"


class EClassroomUpdater(BaseMultiUpdater):
    source = "eclassroom"
    error = ClassroomApiError

    def __init__(self, config: ConfigSourcesEClassroom, session: Session) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.session = session

        super().__init__()

    def get_documents(self) -> Iterator[DocumentInfo]:
        """Get all documents from the e-classroom."""

        self._mark_course_viewed()

        yield from self._get_internal_urls()
        yield from self._get_external_urls()

    def _mark_course_viewed(self) -> None:
        """Mark the course as viewed, so we are not removed for inactivity."""

        params = {
            "moodlewsrestformat": "json",
        }
        data = {
            "courseid": self.config.course,
            "wstoken": self.config.token,
            "wsfunction": "core_course_view_course",
        }

        try:
            response = self.requests.post(self.config.webserviceUrl, params=params, data=data)
            response.raise_for_status()
        except (IOError, ValueError) as error:
            raise ClassroomApiError("Error while accessing e-classroom API") from error

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
            response = self.requests.post(self.config.webserviceUrl, params=params, data=data)
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

                url = self.normalize_url(module["contents"][0]["fileurl"])

                yield DocumentInfo(
                    url=url,
                    type=self._get_document_type(url),
                    title=module["name"],
                    created=datetime.fromtimestamp(module["contents"][0]["timecreated"], tz=timezone.utc),
                    modified=datetime.fromtimestamp(module["contents"][0]["timemodified"], tz=timezone.utc),
                    extension=url.rsplit(".", 1)[1],
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
            response = self.requests.post(self.config.webserviceUrl, params=params, data=data)
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

            url = self.normalize_url(content["externalurl"])

            yield DocumentInfo(
                url=url,
                type=self._get_document_type(url),
                title=content["name"],
                created=datetime.fromtimestamp(content["timemodified"], tz=timezone.utc),
                modified=datetime.fromtimestamp(content["timemodified"], tz=timezone.utc),
                extension=url.rsplit(".", 1)[1],
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

        if document.type == DocumentType.SUBSTITUTIONS:
            return "Nadomeščanja in obvestila"

        if document.type == DocumentType.LUNCH_SCHEDULE:
            return "Razpored kosila"

        assert document.title
        return document.title

    @typing.no_type_check  # Ignored because if regex fails, we cannot do anything
    def get_document_effective(self, document: DocumentInfo) -> date:
        """Return the document effective date in a local timezone."""

        if document.type == DocumentType.SUBSTITUTIONS:
            effective = re.search(r"_obvestila_(.+).pdf", document.url, re.IGNORECASE).group(1)
            return datetime.strptime(effective, "%d._%m._%Y").date()

        if document.type == DocumentType.LUNCH_SCHEDULE:
            title = document.title.split(",")[-1].split("-")[-1].strip()
            search = re.search(r"(\d+) *\. *(\d+) *\. *(\d+)", title)
            return date(year=int(search.group(3)), month=int(search.group(2)), day=int(search.group(1)))

        # This cannot happen because only substitutions and schedules are provided
        raise KeyError("Unknown parsable document type from the e-classroom")

    def document_needs_parsing(self, document: DocumentInfo) -> bool:
        """Return whether the document needs parsing."""

        if document.type == DocumentType.SUBSTITUTIONS or document.type == DocumentType.LUNCH_SCHEDULE:
            return True

        return False

    def document_has_content(self, document: DocumentInfo) -> bool:
        """Return whether the document has content."""

        if document.extension == "docx":
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
            self._parse_substitutions(tables, effective)
        elif document.type == DocumentType.LUNCH_SCHEDULE:
            self._parse_lunch_schedule(tables, effective)
        else:
            # This cannot happen because only menus are provided by the API
            raise KeyError("Unknown parsable document type from the e-classroom")

    @with_span(op="parse", pass_span=True)
    def get_content(self, document: DocumentInfo, content: bytes, span: Span) -> str | None:  # type: ignore[override]
        """Convert content of DOCX circulars to HTML."""

        def ignore_images(_image: Image) -> dict:
            return {}

        # Set basic Sentry span info
        span.set_tag("document.format", "docx")
        span.set_tag("document.type", document.type.value)

        # Convert DOCX to HTML
        result = convert_to_html(io.BytesIO(content), convert_image=ignore_images)
        return typing.cast(str, result.value)

    def _normalize_subject_name(self, name: str) -> str | None:
        """Normalize the subject name."""

        # Special case: Unknown subject
        if self._is_name_empty(name):
            return None

        # Special case: Subject aliases
        if name == "ŠVZS":
            return "ŠVZ"

        # Return the normal name
        return name

    def _normalize_teacher_name(self, name: str) -> str | None:
        """Normalize the teacher name."""

        # Special case: Additional lesson
        if name == "Po urniku ni pouka":
            return None

        # Special case: No teacher
        if name == "samozaposleni":
            return None

        # Special case: Unknown teacher
        if self._is_name_empty(name):
            return None

        # Special case: Multiple Krapež teachers
        if "Krapež" in name:
            if "Alenka" in name:
                return "KrapežA"
            elif "Marjetka" in name:
                return "KrapežM"

        # Special case: Multiple Šajn teachers
        if "Šajn" in name and "Eva" in name:
            return "ŠajnE"

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

    def _normalize_classroom_name(self, name: str) -> str | None:
        """Normalize the classroom name."""

        # Special case: Unknown classroom
        if self._is_name_empty(name):
            return None

        # Special case: Classroom aliases
        # Maybe these mappings aren't correct, but who knows...
        if name == "Velika dvorana" or name == "Velika telovadnica":
            return "TV1"
        if name == "Mala dvorana" or name == "Mala telovadnica":
            return "TV3"

        # Return the normal name
        return name

    def _normalize_other_names(self, name: str) -> str | None:
        """Normalize other types of names."""

        return name if not self._is_name_empty(name) else None

    @staticmethod
    def _is_name_empty(name: str) -> bool:
        """Return whether the name is empty."""

        return not name or name == "X" or name == "x" or name == "/" or name == "MANJKA"

    def _format_substitution(
        self,
        effective: date,
        day: int,
        time: int,
        subject: str | None,
        notes: str | None,
        original_teacher: str | None,
        original_classroom: str | None,
        class_: str | None,
        teacher: str | None,
        classroom: str | None,
    ) -> dict[str, Any]:
        """Format the substitution into a dict that can be stored to a database."""

        # fmt: off
        return {
            "date": effective,
            "day": day,
            "time": time,
            "subject": subject,
            "notes": notes,
            "original_teacher_id": get_or_create(self.session, model=Teacher, name=original_teacher)[0].id if original_teacher else None,
            "original_classroom_id": get_or_create(self.session, model=Classroom, name=original_classroom)[0].id if original_classroom else None,
            "class_id": get_or_create(self.session, model=Class, name=class_)[0].id if class_ else None,
            "teacher_id": get_or_create(self.session, model=Teacher, name=teacher)[0].id if teacher else None,
            "classroom_id": get_or_create(self.session, model=Classroom, name=classroom)[0].id if classroom else None,
        }
        # fmt: on

    def _parse_substitutions(self, tables: Tables, effective: date) -> None:
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
            for row0 in table:
                # We use different variable name here, otherwise mypy complains
                row = [column.replace("\n", " ").strip() if column else "" for column in row0]

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
                elif "Oddelek" in row[0] or "Razred" in row[0] or "dijaki" in row[0]:
                    parser_type = ParserType.UNKNOWN
                    continue

                # Skip empty rows
                if not any(row) or not row[1]:
                    continue

                # Parse substitutions
                if parser_type == ParserType.SUBSTITUTUONS:
                    # Get basic substitution properties
                    time = int(row[1][:-1]) if row[1] != "PU" else 0
                    subject = self._normalize_subject_name(row[5])
                    notes = self._normalize_other_names(row[6])

                    # Get the original teacher if it is specified
                    # Otherwise, use the last specified original teacher
                    # fmt: off
                    original_teacher = self._normalize_teacher_name(row[0]) if row[0] else last_original_teacher
                    last_original_teacher = original_teacher
                    # fmt: on

                    # Get the new teacher
                    teacher = self._normalize_teacher_name(row[4])

                    # Get the classroom (which stays the same)
                    # There may be multiple classrooms per row
                    classrooms = [self._normalize_classroom_name(name) for name in row[3].split(", ")]

                    # Handle multiple classes
                    classes = row[2].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    # fmt: off
                    for class_, classroom in product(classes, classrooms):
                        substitutions.append(self._format_substitution(
                            effective, day, time,
                            subject, notes,
                            original_teacher, classroom,
                            class_, teacher, classroom,
                        ))
                    # fmt: on

                elif parser_type == ParserType.LESSON_CHANGE:
                    # Get basic substitution properties
                    time = int(row[1][:-1]) if row[1] != "PU" else 0
                    subject = self._normalize_subject_name(row[3].split(" → ")[1])
                    notes = self._normalize_other_names(row[5])

                    # Get the original and the new teacher
                    original_teacher = self._normalize_teacher_name(row[2].split(" → ")[0])
                    teacher = self._normalize_teacher_name(row[2].split(" → ")[1])

                    # Get the original and the new classrooms
                    # They are commonly the same, but not always
                    # There may also be multiple classrooms per row
                    split_classrooms = row[4].split(" → ")
                    original_classrooms = []
                    classrooms = []

                    if len(split_classrooms) == 1:
                        # Classroom has stayed the same
                        # fmt: off
                        original_classrooms = [self._normalize_classroom_name(name) for name in split_classrooms[0].split(", ")]
                        classrooms = original_classrooms
                        # fmt: on

                    elif len(split_classrooms) == 2:
                        # Classroom has changed
                        # fmt: off
                        original_classrooms = [self._normalize_classroom_name(name) for name in split_classrooms[0].split(", ")]
                        classrooms = [self._normalize_classroom_name(name) for name in split_classrooms[1].split(", ")]
                        # fmt: on

                    # Handle multiple classes
                    classes = row[0].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    # fmt: off
                    for class_, original_classroom, classroom in product(classes, original_classrooms, classrooms):
                        substitutions.append(self._format_substitution(
                            effective, day, time,
                            subject, notes,
                            original_teacher, original_classroom,
                            class_, teacher, classroom,
                        ))
                    # fmt: on

                elif parser_type == ParserType.SUBJECT_CHANGE:
                    # Get basic substitution properties
                    time = int(row[1][:-1]) if row[1] != "PU" else 0
                    subject = self._normalize_subject_name(row[3].split(" → ")[1])
                    notes = self._normalize_other_names(row[5])

                    # Get the teacher (which stays the same)
                    original_teacher = self._normalize_teacher_name(row[2])
                    teacher = original_teacher

                    # Get the classroom (which stays the same)
                    original_classroom = self._normalize_classroom_name(row[4])
                    classroom = original_classroom

                    # Handle multiple classes
                    classes = row[0].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    # fmt: off
                    for class_ in classes:
                        substitutions.append(self._format_substitution(
                            effective, day, time,
                            subject, notes,
                            original_teacher, original_classroom,
                            class_, teacher, classroom,
                        ))
                    # fmt: on

                elif parser_type == ParserType.CLASSROOM_CHANGE:
                    # Get basic substitution properties
                    time = int(row[1][:-1]) if row[1] != "PU" else 0
                    subject = self._normalize_subject_name(row[3])
                    notes = self._normalize_other_names(row[6])

                    # Get the teacher (which stays the same)
                    original_teacher = self._normalize_teacher_name(row[2])
                    teacher = original_teacher

                    # Get the original and the new classrooms
                    # fmt: off
                    original_classrooms = [self._normalize_classroom_name(name) for name in row[4].split(", ")]
                    classrooms = [self._normalize_classroom_name(name) for name in row[5].split(", ")]
                    # fmt: on

                    # Handle multiple classes
                    classes = row[0].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    # fmt: off
                    for class_, original_classroom, classroom in product(classes, original_classrooms, classrooms):
                        substitutions.append(self._format_substitution(
                            effective, day, time,
                            subject, notes,
                            original_teacher, original_classroom,
                            class_, teacher, classroom,
                        ))
                    # fmt: on

        # Deduplicate substitutions
        substitutions = [dict(subs2) for subs2 in {tuple(subs1.items()) for subs1 in substitutions}]

        # Remove old substitutions from a database
        self.session.query(Substitution).filter(Substitution.date == effective).delete()

        # Store new substitutions to a database
        if substitutions:
            self.session.execute(insert(Substitution), substitutions)

    def _parse_lunch_schedule(self, tables: Tables, effective: date) -> None:
        """Parse the lunch schedule document."""

        schedule = []

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

                # Handle incorrectly connected cells
                if row[0] and " " in row[0] and len(row) == 4:
                    time, notes = row[0].split(" ", 1)
                    row[0] = time
                    row.insert(1, notes)

                # Skip the header
                if row[0] and "ura" in row[0]:
                    continue

                # Skip empty rows
                if len(row) != 5 or not row[0]:
                    continue

                # Skip invalid time formats
                if "odj." in row[0]:
                    continue

                # Handle multiple times in the same cell
                times = row[0].split("\n", 1)
                if len(times) == 2:
                    row[0] = times[0]
                    table[index + 1][0] = times[1]

                # Handle incorrectly connected cells
                if row[1] is None and len(row[0].split(" ", 1)) == 2:
                    row[0], row[1] = row[0].split(" ", 1)

                # Parse time format
                time = re.sub("cca|do", "", row[0]).replace(".", ":").strip()
                time = datetime.strptime(time, "%H:%M").time()  # type: ignore[assignment]

                # Get notes, classes and location if they are specified
                notes = row[1].strip() if row[1] else None  # type: ignore[assignment]
                classes = re.sub("[().]", "", row[2]).split(",") if row[2] else []
                location = row[4].strip() if row[4] else None

                # Handle special format for multiple classes
                if len(classes) == 1 and isinstance(classes[0], str):
                    if search := re.search(r"(\d)\.? ?[lL]?(?:\.|$)", classes[0]):
                        class_letters = ["A", "B", "C", "D", "E", "F"]
                        classes = [search.group(1) + class_ for class_ in class_letters]

                for class_ in classes:
                    if not class_.strip():
                        continue

                    class_id = get_or_create(self.session, model=Class, name=class_.strip())[0].id

                    schedule.append(
                        {
                            "class_id": class_id,
                            "date": effective,
                            "time": time,
                            "location": location,
                            "notes": notes,
                        }
                    )

        # Store schedule to a database
        self.session.query(LunchSchedule).filter(LunchSchedule.date == effective).delete()
        self.session.execute(insert(LunchSchedule), schedule)
