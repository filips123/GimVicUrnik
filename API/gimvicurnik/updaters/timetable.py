from __future__ import annotations

import logging
import re
import typing
from collections import defaultdict
from datetime import datetime
from hashlib import sha256

import requests
from sqlalchemy import insert

from ..database import Class, Classroom, Document, DocumentType, Lesson, Teacher
from ..errors import TimetableApiError
from ..utils.database import get_or_create
from ..utils.sentry import sentry_available, with_span

if typing.TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from sentry_sdk.tracing import Span
    from ..config import ConfigSourcesTimetable


class TimetableUpdater:
    def __init__(self, config: ConfigSourcesTimetable, session: Session) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.session = session

    def update(self) -> None:
        """Update the timetable."""

        try:
            self._handle()  # type: ignore[call-arg]

        except Exception as error:
            if sentry_available:
                import sentry_sdk

                # fmt: off
                sentry_sdk.set_context("document", {
                    "URL": self.config.url,
                    "source": DocumentType.TIMETABLE.value,
                    "type​": DocumentType.TIMETABLE.value
                })
                # fmt: on

                sentry_sdk.set_tag("document_source", DocumentType.TIMETABLE.value)
                sentry_sdk.set_tag("document_type", DocumentType.TIMETABLE.value)

            self.logger.exception(error)

    @with_span(op="document", pass_span=True)
    def _handle(self, span: Span) -> None:
        """Handle the timetable document."""

        span.description = self.config.url
        span.set_tag("document.url", self.config.url)
        span.set_tag("document.source", DocumentType.TIMETABLE.value)
        span.set_tag("document.type", DocumentType.TIMETABLE.value)
        span.set_tag("document.action", "crashed")

        # Download the timetable JS and get its hash
        raw_data, new_hash = self._download()

        # Try to find an existing timetable document
        document = (
            self.session.query(Document)
            .filter(Document.type == DocumentType.TIMETABLE, Document.url == self.config.url)
            .first()
        )

        # Skip parsing if the timetable is unchanged
        if document and document.hash == new_hash:
            self.logger.info("Skipped because the timetable is unchanged")
            self.logger.debug("Hash: %s", document.hash)
            self.logger.debug("Last updated: %s", document.modified)

            span.set_tag("document.hash", document.hash)
            span.set_tag("document.modified", document.modified)
            span.set_tag("document.action", "skipped")

            return

        self._parse(document, raw_data, new_hash, span)

    @with_span(op="download")
    def _download(self) -> tuple[str, str]:
        """Download the timetable JS file."""

        try:
            response = requests.get(self.config.url)
            response.raise_for_status()
            content = response.content

        except OSError as error:
            raise TimetableApiError("Error while downloading the timetable") from error

        return content.decode("utf8"), sha256(content).hexdigest()

    @with_span(op="parse")
    def _parse(self, document: Document | None, raw_data: str, new_hash: str, span: Span) -> None:
        """Parse the timetable JS file and store lessons."""

        # Get raw data from timetable file
        data = re.findall(r"podatki\[(\d+)]\[\d] = \"?([^\"\n]*)\"?", raw_data, re.MULTILINE)

        lessons = defaultdict(list)
        for key, value in data:
            lessons[key].append(value.strip())

        # Convert raw data into a model
        # fmt: off
        models = [
            {
                "day": lesson[5],
                "time": lesson[6],
                "subject": lesson[3] if lesson[3] else None,
                "class_id": get_or_create(self.session, model=Class, name=lesson[1])[0].id if lesson[1] else None,
                "teacher_id": get_or_create(self.session, model=Teacher, name=lesson[2])[0].id if lesson[2] else None,
                "classroom_id": get_or_create(self.session, model=Classroom, name=lesson[4])[0].id if lesson[4] else None,
            }
            for _, lesson in lessons.items()
        ]
        # fmt: on

        self.session.query(Lesson).delete()
        self.session.execute(insert(Lesson), models)

        # Update or create a document
        if not document:
            document = Document()
            created = True
        else:
            created = False

        document.type = DocumentType.TIMETABLE
        document.modified = datetime.utcnow()
        document.url = self.config.url
        document.hash = new_hash
        self.session.add(document)

        span.set_tag("document.hash", document.hash)
        span.set_tag("document.modified", document.modified)
        span.set_tag("document.action", "created" if created else "updated")

        self.logger.info("Finished updating the timetable")
