from __future__ import annotations

import logging
import typing

from datetime import timedelta, date as date_
from hashlib import sha256
from itertools import product
from random import getrandbits
import json

import requests
from sqlalchemy import insert

from ..database import DocumentType, Substitution
from ..errors import SolsisApiError
from ..utils.normalizers import (
    normalize_subject_name,
    normalize_teacher_name,
    normalize_classroom_name,
    normalize_other_names,
    format_substitution,
)
from ..utils.sentry import sentry_available, with_span

if typing.TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from ..config import ConfigSourcesSolsis


class SolsisUpdater:
    source = "solsis"

    # fmt: off
    def __init__(self, config: ConfigSourcesSolsis, session: Session, date_from: date_, date_to: date_) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.session = session

        self.date_from = date_from
        self.date_to = date_to
    # fmt: on

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
                    "type": DocumentType.SUBSTITUTIONS.value
                })
                # fmt: on

                sentry_sdk.set_tag("document_source", self.source)
                sentry_sdk.set_tag("document_type", DocumentType.SUBSTITUTIONS.value)

            self.logger.exception(error)

    def get_substitutions(self) -> None:
        # Generate span of dates
        dates = [self.date_from + timedelta(days=i) for i in range((self.date_to - self.date_from).days + 1)]

        for date in dates:
            # Download the Solsis JSON
            json_data = self._download_substitutions(date)

            # Load the Solsis JSON
            solsis_substitutions = json.loads(json_data)

            # Skip empty substitutions as the API returns only the date
            if "nadomescanja" not in solsis_substitutions:
                continue

            day = date.isoweekday()
            substitutions = []

            # Loop trough the Solsis substitutions sections and construct models applicable to our database
            for substitution in solsis_substitutions["nadomescanja"]:
                original_teacher = normalize_teacher_name(substitution["odsoten_fullname"])

                # Teacher is absent
                for substitution_lesson in substitution["nadomescanja_ure"]:
                    time = int(substitution_lesson["ura"][:-1]) if substitution_lesson["ura"] != "PU" else 0
                    subject = normalize_subject_name(substitution_lesson["predmet"])
                    notes = normalize_other_names(substitution_lesson["opomba"])

                    # New teacher
                    teacher = normalize_teacher_name(substitution_lesson["nadomesca_full_name"])

                    # Handle multiple classrooms
                    # fmt: off
                    classrooms = [normalize_classroom_name(name) for name in substitution_lesson["ucilnica"].split(", ")]
                    # fmt: on

                    # Handle multiple classes
                    classes = substitution_lesson["class_name"].replace(". ", "").split(" - ")
                    classes = classes[:-1] if len(classes) > 1 else classes

                    for class_, classroom in product(classes, classrooms):
                        substitutions.append(
                            format_substitution(
                                self.session,
                                date,
                                day,
                                time,
                                subject,
                                notes,
                                original_teacher,
                                classroom,
                                class_,
                                teacher,
                                classroom,
                            )
                        )

            # Subject change
            for substitution in solsis_substitutions["menjava_predmeta"]:
                time = int(substitution["ura"][:-1]) if substitution["ura"] != "PU" else 0
                subject = normalize_subject_name(substitution["predmet"])
                notes = normalize_other_names(substitution["opomba"])

                teacher = normalize_teacher_name(substitution["ucitelj"])

                # Handle multiple classrooms
                # fmt: off
                classrooms = [normalize_classroom_name(name) for name in substitution["ucilnica"].split(", ")]
                # fmt: on

                # Handle multiple classes
                classes = substitution["class_name"].replace(". ", "").split(" - ")
                classes = classes[:-1] if len(classes) > 1 else classes

                for class_, classroom in product(classes, classrooms):
                    substitutions.append(
                        format_substitution(
                            self.session,
                            date,
                            day,
                            time,
                            subject,
                            notes,
                            teacher,
                            classroom,
                            class_,
                            teacher,
                            classroom,
                        )
                    )

            # Lesson change
            for substitution in solsis_substitutions["menjava_ur"]:
                time = int(substitution["ura"][:-1]) if substitution["ura"] != "PU" else 0
                subject = normalize_subject_name(substitution["predmet"].split(" -> ")[1])
                notes = normalize_other_names(substitution["opomba"])

                # Handle teacher change
                split_teachers = substitution["zamenjava_uciteljev"].split(" -> ")

                original_teacher = normalize_teacher_name(split_teachers[0])
                teacher = normalize_teacher_name(split_teachers[1])

                # Handle classrooms change
                split_classrooms = substitution["ucilnica"].split(" -> ")

                # fmt: off
                original_classrooms = [normalize_classroom_name(name) for name in split_classrooms[0].split(", ")]
                # fmt: on

                # Check if the classrooms have changed
                if len(split_classrooms) == 2:
                    classrooms = [normalize_classroom_name(name) for name in split_classrooms[1].split(", ")]
                else:
                    classrooms = original_classrooms

                # Handle multiple classes
                classes = substitution["class_name"].replace(". ", "").split(" - ")
                classes = classes[:-1] if len(classes) > 1 else classes

                # fmt: off
                for class_, original_classroom, classroom in product(classes, original_classrooms, classrooms):
                    substitutions.append(
                        format_substitution(
                            self.session,
                            date,
                            day,
                            time,
                            subject,
                            notes,
                            original_teacher,
                            original_classroom,
                            class_,
                            teacher,
                            classroom,
                        )
                    )
                # fmt: on

            # Classroom change
            for substitution in solsis_substitutions["menjava_ucilnic"]:
                time = int(substitution["ura"][:-1]) if substitution["ura"] != "PU" else 0
                subject = normalize_subject_name(substitution["predmet"])
                notes = normalize_other_names(substitution["opomba"])

                teacher = normalize_teacher_name(substitution["ucitelj"])

                # Handle multiple classrooms
                # fmt: off
                original_classrooms = [normalize_classroom_name(name) for name in substitution["ucilnica_from"].split(", ")]
                classrooms = [normalize_classroom_name(name) for name in substitution["ucilnica_to"].split(", ")]
                # fmt: off

                # Skip if the classrooms have not changed
                if classrooms == original_classrooms:
                    continue

                # Handle multiple classes
                classes = substitution["class_name"].replace(". ", "").split(" - ")
                classes = classes[:-1] if len(classes) > 1 else classes

                # fmt: off
                for class_, original_classroom, classroom in product(classes, original_classrooms, classrooms):
                    substitutions.append(
                        format_substitution(
                            self.session,
                            date,
                            day,
                            time,
                            subject,
                            notes,
                            teacher,
                            original_classroom,
                            class_,
                            teacher,
                            classroom,
                        )
                    )
                # fmt: on

            # Deduplicate substitutions
            substitutions = [dict(subs2) for subs2 in {tuple(subs1.items()) for subs1 in substitutions}]

            # Remove old substitutions from the database
            self.session.query(Substitution).filter(Substitution.date == date).delete()

            # Store new substitutions to the database
            if substitutions:
                self.session.execute(insert(Substitution), substitutions)

    @with_span(op="download")
    def _download_substitutions(self, date: date_) -> str:
        """Download the Solsis JSON file."""

        # Every request needs a different nonsense
        nonsense = "%032x" % getrandbits(128)

        # Compose the url
        params = f"func=gateway&call=suplence&datum={date.strftime('%Y-%m-%d')}&nonsense={nonsense}"
        signature_string = f"{self.config.serverName}||{params}||{self.config.apiKey}"
        signature = sha256(signature_string.encode()).hexdigest()
        url = f"{self.config.url}?{params}&signature={signature}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.content

        except OSError as error:
            raise SolsisApiError("Error while downloading the Solsis substitutions") from error

        return content.decode("utf8")
