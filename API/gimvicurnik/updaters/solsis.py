from __future__ import annotations

import logging
import typing

from datetime import timedelta, date as date_
from hashlib import sha256
from random import getrandbits
import json

import requests
from sqlalchemy import insert

from ..database import Classroom, Class, DocumentType, Substitution, Teacher
from ..errors import SolsisApiError
from ..utils.database import get_or_create
from ..utils.sentry import sentry_available, with_span

if typing.TYPE_CHECKING:
    from typing import Any
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
                original_teacher = self._normalize_teacher_name(substitution["odsoten_fullname"])

                # Teacher is absent
                for substitution_lesson in substitution["nadomescanja_ure"]:
                    time = int(substitution_lesson["ura"][:-1]) if substitution_lesson["ura"] != "PU" else 0
                    subject = self._normalize_subject_name(substitution_lesson["predmet"])
                    notes = self._normalize_other_names(substitution_lesson["opomba"])

                    teacher = self._normalize_teacher_name(substitution_lesson["nadomesca_full_name"])
                    classroom = self._normalize_classroom_name(substitution_lesson["ucilnica"])

                    # Handle multiple classes
                    classes = substitution_lesson["class_name"].replace(". ", "").split(" - ")

                    for class_ in classes:
                        substitutions.append(
                            self._format_substitution(
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
                subject = self._normalize_subject_name(substitution["predmet"])
                notes = self._normalize_other_names(substitution["opomba"])

                teacher = self._normalize_teacher_name(substitution["ucitelj"])
                classroom = self._normalize_classroom_name(substitution["ucilnica"])

                # Handle multiple classes
                classes = substitution["class_name"].replace(". ", "").split(" - ")

                for class_ in classes:
                    substitutions.append(
                        self._format_substitution(
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

            # Time change
            for substitution in solsis_substitutions["menjava_ur"]:
                time = int(substitution_lesson["ura"][:-1]) if substitution["ura"] != "PU" else 0
                subject = self._normalize_subject_name(substitution["predmet"].split(" -> ")[1])
                notes = self._normalize_other_names(substitution["opomba"])

                teachers = substitution["zamenjava_uciteljev"].split(" -> ")
                classrooms = substitution["ucilnica"].split(" -> ")

                original_teacher = self._normalize_teacher_name(teachers[0])
                teacher = self._normalize_teacher_name(teachers[1])

                original_classroom = self._normalize_teacher_name(classrooms[0])
                classroom = self._normalize_teacher_name(
                    classrooms[1] if len(classrooms) == 2 else classrooms[0]
                )

                # Handle multiple classes
                classes = substitution["class_name"].replace(". ", "").split(" - ")

                for class_ in classes:
                    substitutions.append(
                        self._format_substitution(
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

            # Classroom change
            for substitution in solsis_substitutions["menjava_ucilnic"]:
                time = int(substitution["ura"][:-1]) if substitution["ura"] != "PU" else 0
                subject = self._normalize_subject_name(substitution["predmet"])
                notes = self._normalize_other_names(substitution["opomba"])

                teacher = self._normalize_teacher_name(substitution["ucitelj"])

                original_classroom = self._normalize_classroom_name(substitution["ucilnica_from"])
                classroom = self._normalize_classroom_name(substitution["ucilnica_to"])

                # Skip if the classroom has not changed
                if classroom == original_classroom:
                    continue

                # Handle multiple classes
                classes = substitution["class_name"].replace(". ", "").split(" - ")

                for class_ in classes:
                    substitutions.append(
                        self._format_substitution(
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
        date: date_,
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
            "date": date,
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
