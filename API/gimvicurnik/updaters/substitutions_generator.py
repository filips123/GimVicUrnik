import datetime
import hashlib
import logging
import os
import re
import tempfile
from random import randint, choice
import random

import requests
from pdf2docx import extract_tables

from ..database import Class, Classroom, Document, LunchSchedule, Substitution, Teacher
from ..errors import ClassroomApiError, InvalidRecordError, InvalidTokenError, LunchScheduleError
from ..utils.database import get_or_create
from ..utils.sentry import with_span
from ..utils.url import normalize_url, tokenize_url


class subgen:
    def __init__(self, config, session, number):
        self.session = session
        self.logger = logging.getLogger(__name__)
        self.number = int(number)

    def update(self):
        self._store_substitutions(self.number)

    @with_span(op="document")
    def _store_substitutions(self, number):

        substitutions = []

        parser_type = None
        last_original_teacher = None

        # Parse tables into substitutions
        for x in range(number, startrange=0, endrange=14):
            date = datetime.datetime.now() + datetime.timedelta(days=randint(startrange, endrange))
            day = date.isoweekday()
            substitutions.append(
                {
                    "date": date,
                    "day": day,
                    "time": randint(0, 8),
                    "subject": choice(["MAT", "SLO", "ANG", "NEM", "KEM", "FIZ"]),
                    "original_teacher_id": self.session.query(Teacher)[
                        random.randrange(0, self.session.query(Teacher).count())
                    ].id,
                    "original_classroom_id": self.session.query(Classroom)[
                        random.randrange(0, self.session.query(Classroom).count())
                    ].id,
                    "class_id": self.session.query(Class)[random.randrange(0, self.session.query(Class).count())].id,
                    "teacher_id": self.session.query(Teacher)[random.randrange(0, self.session.query(Teacher).count())].id,
                    "classroom_id": self.session.query(Classroom)[random.randrange(0, self.session.query(Classroom).count())].id,
                }
            )

        # Store substitutions in database
        substitutions = [dict(element) for element in {tuple(substitution.items()) for substitution in substitutions}]

        self.session.query(Substitution).filter(Substitution.date == date).delete()
        self.session.bulk_insert_mappings(Substitution, substitutions)

    @staticmethod
    def _normalize_teacher_name(name):
        # Special case: Additional lesson
        if name == "Po urniku ni pouka":
            return None

        # Special case: Unknown teacher
        if name == "X" or name == "x" or name == "/":
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
            "Vičar": "Potočnik",
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
        if name == "X" or name == "x" or name == "/":
            return None

        return name
