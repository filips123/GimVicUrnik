from __future__ import annotations

import logging
import typing
from datetime import date as date_, timedelta
from hashlib import sha256
from itertools import product
from random import getrandbits

import requests
from sqlalchemy import insert

from ..database import DocumentType, Substitution
from ..errors import SolsisApiError
from ..utils.normalizers import (
    format_substitution,
    normalize_classroom_name,
    normalize_other_names,
    normalize_subject_name,
    normalize_teacher_name,
)
from ..utils.sentry import sentry_available, with_span

if typing.TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from ..config import ConfigSourcesSolsis


class TypeSubstitutions(typing.TypedDict):
    odsoten_fullname: str
    stevilo_ur_nadomescanj: int
    nadomescanja_ure: list[TypeSubstitutionLessons]
    style_index: int


class TypeSubstitutionLessons(typing.TypedDict):
    ura: str
    class_name: str
    sproscen_class_name: str
    predmet: str
    nadomesca_full_name: str
    ucilnica: str
    sproscen: int
    zaposli: int
    opomba: str


class TypeSubjectChange(typing.TypedDict):
    class_name: str
    ura: str
    original_predmet: str
    predmet: str
    ucitelj: str
    ucilnica: str
    opomba: str
    style_index: int


class TypeLessonChange(typing.TypedDict):
    class_name: str
    ura: str
    predmet: str
    zamenjava_uciteljev: str
    ucilnica: str
    opomba: str
    style_index: int


class TypeClassroomChange(typing.TypedDict):
    class_name: str
    ura: str
    predmet: str
    ucitelj: str
    ucilnica_from: str
    ucilnica_to: str
    opomba: str
    style_index: int


class TypeMoreTeachers(typing.TypedDict):
    ura: str
    class_name: str
    ucitelj: str
    ucilnica: str
    opomba: str
    style_index: int


class TypeReservation(typing.TypedDict):
    ura: str
    ucilnica: str
    rezervator: str
    opomba: str
    style_index: int


class TypeRoot(typing.TypedDict, total=False):
    nadomescanja: list[TypeSubstitutions]
    menjava_predmeta: list[TypeSubjectChange]
    menjava_ur: list[TypeLessonChange]
    menjava_ucilnic: list[TypeClassroomChange]
    rezerviranje_ucilnice: list[TypeReservation]
    vec_uciteljev_v_razredu: list[TypeMoreTeachers]
    seznam_manjkajocih_razredov: list[str]
    datum: str


class SolsisUpdater:
    source = "solsis"

    def __init__(
        self,
        config: ConfigSourcesSolsis,
        session: Session,
        date_from: date_,
        date_to: date_,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.session = session

        self.date_from = date_from
        self.date_to = date_to

    def update(self) -> None:
        """Update Solsis files."""

        try:
            self.get_substitutions()

        except Exception as error:
            if sentry_available:
                import sentry_sdk

                # fmt: off
                sentry_sdk.set_context("document", {
                    "URL": self.config.url,
                    "source": self.source,
                    "type​": DocumentType.SUBSTITUTIONS.value
                })
                # fmt: on

                sentry_sdk.set_tag("document_source", self.source)
                sentry_sdk.set_tag("document_type", DocumentType.SUBSTITUTIONS.value)

            self.logger.exception(error)

    def get_substitutions(self) -> None:
        # Generate span of dates
        dates = [self.date_from + timedelta(days=i) for i in range((self.date_to - self.date_from).days + 1)]

        for date in dates:
            self.logger.info("Handling substitutions for %s", date, extra={"date": date})

            # Download and parse the Solsis JSON
            solsis_substitutions: TypeRoot = self._download_substitutions(date)

            # Skip empty substitutions as the API returns only the date
            if "nadomescanja" not in solsis_substitutions:
                continue

            day = date.isoweekday()
            substitutions = []

            # Loop through the Solsis substitutions sections and construct models for a database

            # Substitutions (Teacher is absent)
            for substitution in solsis_substitutions["nadomescanja"]:
                # Get the original teacher
                original_teacher = normalize_teacher_name(substitution["odsoten_fullname"])

                for lesson in substitution["nadomescanja_ure"]:
                    # Get basic substitution properties
                    time = int(lesson["ura"][:-1]) if lesson["ura"] != "PU" else 0
                    subject = normalize_subject_name(lesson["predmet"])
                    notes = normalize_other_names(lesson["opomba"])

                    # Get the new teacher
                    teacher = normalize_teacher_name(lesson["nadomesca_full_name"])

                    # Get the classroom (which stays the same)
                    # There may be multiple classrooms per entry
                    classrooms = [normalize_classroom_name(name) for name in lesson["ucilnica"].split(", ")]

                    # Handle multiple classes
                    classes = lesson["class_name"].upper().replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    # fmt: off
                    for class_, classroom in product(classes, classrooms):
                        substitutions.append(format_substitution(
                            self.session,
                            date, day, time,
                            subject, notes,
                            original_teacher, classroom,
                            class_, teacher, classroom,
                        ))
                    # fmt: on

            # Subject change
            for substitution in solsis_substitutions["menjava_predmeta"]:
                # Get basic substitution properties
                time = int(substitution["ura"][:-1]) if substitution["ura"] != "PU" else 0
                subject = normalize_subject_name(substitution["predmet"])
                notes = normalize_other_names(substitution["opomba"])

                # Get the teacher (which stays the same)
                teacher = normalize_teacher_name(substitution["ucitelj"])

                # Get the classroom (which stays the same)
                # There may be multiple classrooms per entry
                classrooms = [normalize_classroom_name(name) for name in substitution["ucilnica"].split(", ")]

                # Handle multiple classes
                classes = substitution["class_name"].upper().replace(". ", "").split(" - ")
                classes = classes[:-1] if len(classes) > 1 else classes

                # fmt: off
                for class_, classroom in product(classes, classrooms):
                    substitutions.append(
                        format_substitution(
                            self.session,
                            date, day, time,
                            subject, notes,
                            teacher, classroom,
                            class_, teacher, classroom,
                        )
                    )
                # fmt: on

            # Lesson change
            for substitution in solsis_substitutions["menjava_ur"]:
                # Get basic substitution properties
                time = int(substitution["ura"][:-1]) if substitution["ura"] != "PU" else 0
                subject = normalize_subject_name(substitution["predmet"].split(" -> ")[1])
                notes = normalize_other_names(substitution["opomba"])

                # Get the original and the new teacher
                split_teachers = substitution["zamenjava_uciteljev"].split(" -> ")
                original_teacher = normalize_teacher_name(split_teachers[0])
                teacher = normalize_teacher_name(split_teachers[1])

                # Handle classrooms change
                split_classrooms = substitution["ucilnica"].split(" -> ")

                # Get the original classrooms
                # fmt: off
                original_classrooms = [normalize_classroom_name(name) for name in split_classrooms[0].split(", ")]
                # fmt: on

                # Check if the classrooms have changed
                if len(split_classrooms) == 2:
                    classrooms = [normalize_classroom_name(name) for name in split_classrooms[1].split(", ")]
                else:
                    classrooms = original_classrooms

                # Handle multiple classes
                classes = substitution["class_name"].upper().replace(". ", "").split(" - ")
                classes = classes[:-1] if len(classes) > 1 else classes

                # fmt: off
                for class_, original_classroom, classroom in product(classes, original_classrooms, classrooms):
                    substitutions.append(
                        format_substitution(
                            self.session,
                            date, day, time,
                            subject, notes,
                            original_teacher, original_classroom,
                            class_, teacher, classroom,
                        )
                    )
                # fmt: on

            # Classroom change
            for substitution in solsis_substitutions["menjava_ucilnic"]:
                # Get basic substitution properties
                time = int(substitution["ura"][:-1]) if substitution["ura"] != "PU" else 0
                subject = normalize_subject_name(substitution["predmet"])
                notes = normalize_other_names(substitution["opomba"])

                # Get the teacher (which stays the same)
                teacher = normalize_teacher_name(substitution["ucitelj"])

                # Get the original and the new classrooms
                # fmt: off
                original_classrooms = [normalize_classroom_name(name) for name in substitution["ucilnica_from"].split(", ")]
                classrooms = [normalize_classroom_name(name) for name in substitution["ucilnica_to"].split(", ")]
                # fmt: off

                # Handle multiple classes
                classes = substitution["class_name"].upper().replace(". ", "").split(" - ")
                classes = classes[:-1] if len(classes) > 1 else classes

                # fmt: off
                for class_, original_classroom, classroom in product(classes, original_classrooms, classrooms):
                    if original_classroom == classroom:
                        continue

                    substitutions.append(
                        format_substitution(
                            self.session,
                            date, day, time,
                            subject, notes,
                            teacher, original_classroom,
                            class_, teacher, classroom,
                        )
                    )
                # fmt: on

            # Deduplicate substitutions
            substitutions = list({frozenset(subs.items()): subs for subs in substitutions}.values())

            # Remove old substitutions from the database
            self.session.query(Substitution).filter(Substitution.date == date).delete()

            # Store new substitutions to the database
            if substitutions:
                self.session.execute(insert(Substitution), substitutions)

    @with_span(op="download")
    def _download_substitutions(self, date: date_) -> TypeRoot:
        """Download and parse the Solsis JSON file."""

        # Every request needs a different nonsense
        nonsense = "%032x" % getrandbits(128)

        # Compose the URL
        params = f"func=gateway&call=suplence&datum={date.strftime('%Y-%m-%d')}&nonsense={nonsense}"
        signature_string = f"{self.config.serverName}||{params}||{self.config.apiKey}"
        signature = sha256(signature_string.encode()).hexdigest()
        url = f"{self.config.url}?{params}&signature={signature}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return typing.cast(TypeRoot, response.json())

        except (OSError, ValueError) as error:
            raise SolsisApiError("Error while downloading substitutions from Solsis API") from error
