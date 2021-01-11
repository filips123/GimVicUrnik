import datetime
import hashlib
import logging
import re
from collections import defaultdict

import requests

from ..database import Class, Classroom, Document, Lesson, Teacher
from ..errors import TimetableApiError
from ..utils.database import get_or_create


class TimetableUpdater:
    raw = None
    hash = None

    def __init__(self, config, session):
        self.url = config["url"]
        self.session = session
        self.logger = logging.getLogger(__name__)

    def update(self):
        self._download()
        self._parse()

    def _download(self):
        try:
            response = requests.get(self.url)
            content = response.content

            response.raise_for_status()
        except IOError as error:
            raise TimetableApiError("Error while downloading timetable") from error

        self.raw = content.decode("utf8")
        self.hash = str(hashlib.sha256(content).hexdigest())

    def _parse(self):
        # Skip parsing if the timetable is unchanged
        document = self.session.query(Document).filter(Document.type == "timetable", Document.url == self.url).first()
        if self.hash == getattr(document, "hash", False):
            self.logger.info("Skipped because the timetable is unchanged")
            self.logger.debug("Hash: %s", document.hash)
            self.logger.debug("Last updated: %s", document.date)

            return

        # Get raw data from timetable file
        regex = r'podatki\[([0-9]+)\]\[[0-9]\] = "?([^"\n]*)"?'
        data = re.findall(regex, self.raw, re.MULTILINE)

        lessons = defaultdict(list)
        for key, value in data:
            lessons[key].append(value.strip())

        # Convert raw data into a model
        models = [
            {
                "day": lesson[5],
                "time": lesson[6],
                "subject": lesson[3] if lesson[3] else None,
                "class_id": get_or_create(self.session, model=Class, name=lesson[1])[0].id if lesson[1] else None,
                "teacher_id": get_or_create(self.session, model=Teacher, name=lesson[2])[0].id if lesson[2] else None,
                "classroom_id": get_or_create(self.session, model=Classroom, name=lesson[4])[0].id
                if lesson[4]
                else None,
            }
            for _, lesson in lessons.items()
        ]

        self.session.query(Lesson).delete()
        self.session.bulk_insert_mappings(Lesson, models)

        # Update or create a document
        if not document:
            document = Document()

        document.date = datetime.datetime.now().date()
        document.type = "timetable"
        document.url = self.url
        document.hash = self.hash

        self.session.add(document)

        self.logger.info("Finished updating the timetable")
