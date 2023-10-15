from __future__ import annotations

import enum
import logging
import os
import re
import typing
from datetime import date, datetime, timezone
from itertools import product
from urllib.parse import urlparse

from mammoth import convert_to_html  # type: ignore
from sqlalchemy import insert
from json import load

from .base import BaseMultiUpdater, DocumentInfo
from ..database import (
    Class,
    Classroom,
    DocumentType,
    Substitution,
    Teacher,
    LunchSchedule,
    SnackMenu,
    Class,
    LunchMenu,
)
from ..errors import (
    ClassroomApiError,
    InvalidRecordError,
    InvalidTokenError,
    SubstitutionsFormatError,
    LunchScheduleFormatError,
    MenuFormatError,
)
from ..utils.database import get_or_create
from ..utils.pdf import extract_tables
from ..utils.sentry import with_span

if typing.TYPE_CHECKING:
    from typing import Any
    from collections.abc import Iterator
    from io import BytesIO
    from mammoth.documents import Image  # type: ignore
    from sqlalchemy.orm import Session
    from sentry_sdk.tracing import Span
    from ..config import ConfigSourcesEClassroom
    from ..utils.pdf import Tables


class ParserType(enum.Enum):
    SUBSTITUTIONS = "substitutions"
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

        except (OSError, ValueError) as error:
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
            response.raise_for_status()
            contents = response.json()

        except (OSError, ValueError) as error:
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

                modified = (
                    datetime.fromtimestamp(module["contents"][0]["timemodified"], tz=timezone.utc)
                    if module["contents"][0]["timemodified"]
                    else None
                )

                created = (
                    datetime.fromtimestamp(module["contents"][0]["timecreated"], tz=timezone.utc)
                    if module["contents"][0]["timecreated"]
                    else modified
                )

                yield DocumentInfo(
                    url=url,
                    type=self._get_document_type(url),
                    title=module["name"],
                    created=created,
                    modified=modified,
                    extension=os.path.splitext(urlparse(url).path)[1][1:],
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
            response.raise_for_status()
            contents = response.json()

        except (OSError, ValueError) as error:
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

            modified = (
                datetime.fromtimestamp(content["timemodified"], tz=timezone.utc)
                if content["timemodified"]
                else None
            )

            yield DocumentInfo(
                url=url,
                type=self._get_document_type(url),
                title=content["name"],
                created=modified,
                modified=modified,
                extension=os.path.splitext(urlparse(url).path)[1][1:],
            )

    @staticmethod
    def _get_document_type(url: str) -> DocumentType:
        """Get a document type based on its URL."""

        if "www.dropbox.com" in url:
            return DocumentType.SUBSTITUTIONS
        elif "razpored-kosila-" in url:
            return DocumentType.LUNCH_SCHEDULE
        elif "malica-" in url:
            return DocumentType.SNACK_MENU
        elif "kosilo-" in url:
            return DocumentType.LUNCH_MENU
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
            .replace("&dl=0", "&raw=1")
            .replace("?rlkey=", "?raw=1&rlkey=")
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

        match document.type:
            case DocumentType.SUBSTITUTIONS:
                return "Nadomeščanja in obvestila"
            case DocumentType.LUNCH_SCHEDULE:
                return "Razpored kosila"
            case DocumentType.SNACK_MENU:
                return "Malica"
            case DocumentType.LUNCH_MENU:
                return "Kosilo"

        assert document.title
        return document.title

    @typing.no_type_check  # Ignored because if regex fails, we cannot do anything
    def get_document_effective(self, document: DocumentInfo) -> date:
        """Return the document effective date in a local timezone."""

        match document.type:
            case DocumentType.SUBSTITUTIONS:
                effective = re.search(r"_obvestila_(.+).pdf", document.url, re.IGNORECASE).group(1)
                return datetime.strptime(effective, "%d._%m._%Y").date()
            case DocumentType.LUNCH_SCHEDULE | DocumentType.SNACK_MENU | DocumentType.LUNCH_MENU:
                search = re.search(r"(\d+)-(\d+)-(\d+)", document.url)
                return date(year=int(search.group(1)), month=int(search.group(2)), day=int(search.group(3)))

        # This cannot happen because only substitutions and schedules are provided
        raise KeyError("Unknown parsable document type from the e-classroom")

    def document_needs_parsing(self, document: DocumentInfo) -> bool:
        """Return whether the document needs parsing."""

        match document.type:
            case DocumentType.SUBSTITUTIONS | DocumentType.LUNCH_SCHEDULE | DocumentType.SNACK_MENU | DocumentType.LUNCH_MENU:
                return True

        return False

    @with_span(op="parse", pass_span=True)
    def parse_document(self, document: DocumentInfo, stream: BytesIO, effective: date, span: Span) -> None:  # type: ignore[override]
        """Parse the document and store extracted data."""

        span.set_tag("document.source", self.source)
        span.set_tag("document.type", document.type.value)
        span.set_tag("document.format", document.extension)

        match (document.type, document.extension):
            case (DocumentType.SUBSTITUTIONS, "pdf"):
                self._parse_substitutions_pdf(stream, effective)
            case (DocumentType.LUNCH_SCHEDULE, "pdf"):
                return
            case (DocumentType.LUNCH_SCHEDULE, "json"):
                self._insert_lunch_schedule_json(stream, effective)
            case (DocumentType.SNACK_MENU, "json"):
                self._insert_snack_menu_json(stream, effective)
            case (DocumentType.LUNCH_MENU, "json"):
                self._insert_lunch_menu_json(stream, effective)
            case (DocumentType.SUBSTITUTIONS, _):
                raise SubstitutionsFormatError(
                    "Unknown substitutions document format: " + str(document.extension)
                )
            case (DocumentType.LUNCH_SCHEDULE, _):
                raise LunchScheduleFormatError(
                    "Unknown lunch schedule document format: " + str(document.extension)
                )
            case (DocumentType.SNACK_MENU, _):
                raise MenuFormatError("Unknown snack menu document format: " + str(document.extension))
            case (DocumentType.LUNCH_MENU, _):
                raise MenuFormatError("Unknown lunch menu document format: " + str(document.extension))
            case _:
                raise KeyError("Unknown parsable document type from the e-classroom")

    def document_needs_extraction(self, document: DocumentInfo) -> bool:
        """Return whether the document content needs to be extracted."""

        # Only DOCX documents (circulars) can have content extracted
        if document.extension == "docx":
            return True

        return False

    @with_span(op="content", pass_span=True)
    def extract_document(self, document: DocumentInfo, content: bytes, span: Span) -> str | None:  # type: ignore[override]
        """Extract the document content and return it as HTML."""

        span.set_tag("document.source", self.source)
        span.set_tag("document.type", document.type.value)
        span.set_tag("document.format", document.extension)

        def ignore_images(_image: Image) -> dict:
            return {}

        # Convert DOCX to HTML
        result = convert_to_html(content, convert_image=ignore_images)
        return typing.cast(str, result.value)

    def _normalize_subject_name(self, name: str) -> str | None:
        """Normalize the subject name."""

        # Special case: Unknown subject
        if self._is_name_empty(name):
            return None

        # Special case: Subject aliases
        if name == "ŠVZS":
            return "ŠVZ"
        elif name == "ŠPVF":
            return "ŠVM"
        elif name == "ŠPVD":
            return "ŠVŽ"

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
        if "Šajn" in name:
            if "Eva" in name:
                return "ŠajnE"
            elif "Majda" in name:
                return "ŠajnM"

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

        # Use only surname
        return name.split()[0]

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

    def _parse_substitutions_pdf(self, stream: BytesIO, effective: date) -> None:
        """Parse the substitutions pdf document."""

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

        # Extract all tables from a PDF stream
        tables = with_span(op="extract")(extract_tables)(stream)

        # Parse tables into substitutions
        for table in tables:
            for row0 in table:
                # We use different variable name here, otherwise mypy complains
                row = [column.replace("\n", " ").strip() if column else "" for column in row0]

                # Get parser type
                if row == header_substitutions:
                    parser_type = ParserType.SUBSTITUTIONS
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
                elif (
                    "Oddelek" in row[0]
                    or "Razred" in row[0]
                    or "dijaki" in row[0]
                    or "RAZREDNIK" in row[1]
                    or "Spoznavanje" in row[1]
                ):
                    parser_type = ParserType.UNKNOWN
                    continue

                # Skip empty rows
                if not any(row) or not row[1]:
                    continue

                # Parse substitutions
                if parser_type == ParserType.SUBSTITUTIONS:
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

    def _insert_lunch_schedule_json(self, stream: BytesIO, effective: date) -> None:
        """Insert the lunch schedule json document."""

        for schedule in load(stream):
            self.session.query(LunchSchedule).filter(LunchSchedule.date == effective).delete()
            self.session.execute(insert(LunchSchedule), schedule)

    def _insert_snack_menu_json(self, stream: BytesIO, effective: date) -> None:
        """Insert the snack menu json document."""

        for menu in load(stream):
            # Get the class id from class name (it will always exist)
            menu["class_id"] = self.session.query(Class).filter(Class.name == menu.class_).first().id  # type: ignore
            del menu["class_"]

            self.session.query(SnackMenu).filter(SnackMenu.date == effective).delete()
            self.session.execute(insert(SnackMenu), menu)

    def _insert_lunch_menu_json(self, stream: BytesIO, effective: date) -> None:
        """Insert the lunch menu json document."""

        for menu in load(stream):
            self.session.query(LunchMenu).filter(LunchMenu.date == effective).delete()
            self.session.execute(insert(LunchMenu), menu)
