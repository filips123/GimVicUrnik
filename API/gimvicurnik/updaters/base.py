from __future__ import annotations

import datetime
import typing
import os
from abc import ABC, abstractmethod
from hashlib import sha256
from io import BytesIO
from urllib.parse import urlparse

import attrs
import requests

from ..database import Document, LunchSchedule, SnackMenu, LunchMenu
from ..utils.sentry import sentry_available, with_span

if typing.TYPE_CHECKING:
    from typing import ClassVar
    from collections.abc import Iterator
    from logging import Logger
    from sqlalchemy.orm import Session
    from sentry_sdk.tracing import Span
    from ..database import DocumentType


@attrs.define(kw_only=True)
class DocumentInfo:
    url: str
    """The document's URL."""

    type: DocumentType
    """The document's type."""

    title: str | None = None
    """
    The document's title.
    May be `None` if cannot be determined.
    """

    created: datetime.datetime | None = None
    """
    The document's created datetime in UTC.
    May be `None` if cannot be determined.
    """

    modified: datetime.datetime | None = None
    """
    The document's modified datetime in UTC.
    May be `None` if cannot be determined.
    """

    extension: str | None = None
    """
    The document file extension.
    May be `None` if cannot be determined.
    """


class BaseMultiUpdater(ABC):
    """Base updater for all sources that can provide multiple documents."""

    source: ClassVar[str]
    """
    An identifier of the updater's source.
    Must be set by subclasses.
    """

    error: ClassVar[type[BaseException]]
    """
    An error that the updater should throw when it cannot access the API.
    Must be set by subclasses and used in its methods whenever needed.
    """

    session: Session
    """
    A database session that the updater should use.
    Must be set by subclasses before running `update`.
    """

    logger: Logger
    """
    A logger that the updater should use.
    Must be set by subclasses before running `update`.
    """

    requests: requests.Session
    """
    A requests session that the updater should use.
    Will be set automatically by the base updater.
    """

    def __init__(self) -> None:
        self.requests = requests.Session()

    def update(self) -> None:
        """Get all available documents and update them."""

        for document in self.get_documents():
            try:
                with self.session.begin_nested():
                    # Decorators that add keyword arguments currently cannot be typed correctly
                    # This seems to be a limitation of Python's typing system and cannot be resolved
                    # Until Python/mypy add support for this, we have to ignore call argument types
                    self.handle_document(document)  # type: ignore[call-arg]
            except Exception as error:
                if sentry_available:
                    import sentry_sdk

                    # fmt: off
                    sentry_sdk.set_context("document", {
                        "URL": document.url,
                        "source": self.source,
                        "type​": document.type.value,
                        "format": document.extension,
                        "created": document.created,
                        "modified": document.modified,
                    })
                    # fmt: on

                    sentry_sdk.set_tag("document_source", self.source)
                    sentry_sdk.set_tag("document_type", document.type.value)
                    sentry_sdk.set_tag("document_format", document.extension)

                self.logger.exception(error)

    @with_span(op="document", pass_span=True)
    def handle_document(self, document: DocumentInfo, span: Span) -> None:
        """
        Store a document to a database and run a parser.

        This function downloads a document and get its content and hash.
        If the document has been changed or needs parsing, the function
        runs a parser from the subclassed updater. If needed, the function
        updates or creates a correct record in a database.

        The subclassed updater must overwrite required methods to determine
        whether a documents needs parsing and how to parse it.
        """

        # == DOCUMENT LOGGING

        # Log the document info
        self.logger.info(
            "Handling a %s document: %s",
            document.type.value,
            document.url,
            extra={
                "url": document.url,
                "source": self.source,
                "type": document.type.value,
                "format": document.extension,
                "created​": document.created,
                "modified​": document.modified,
            },
        )

        # Populate Sentry span tags with document info
        # We set action to crashed but override it later
        span.description = document.url
        span.set_tag("document.url", document.url)
        span.set_tag("document.source", self.source)
        span.set_tag("document.type", document.type.value)
        span.set_tag("document.format", document.extension)
        span.set_tag("document.created", document.created)
        span.set_tag("document.modified", document.modified)
        span.set_tag("document.action", "crashed")

        # == DOCUMENT RECORD (GET)

        # Try to find an existing document record
        record = self.retrieve_document(document)

        # == DOCUMENT PROCESSING

        # Get the modified time if it is set, otherwise use the current time
        created = document.created or datetime.datetime.utcnow()
        modified = document.modified or created

        # Check if the document has changed without downloading it and comparing hashes
        # This may be done by comparing modified dates or other source-specific logic
        # We still compare hashes and skip parsing if needed, even if this returns true
        changed = self.document_has_changed(document, record) if record else True

        # Check if the document needs parsing or content extraction
        parsable = self.document_needs_parsing(document)
        extractable = self.document_needs_extraction(document)

        action = "skipped"
        effective = None
        content = None
        crashed = False
        new_hash = None

        if changed and (parsable or extractable):
            # Download the document and get its content and hash
            # If this fails, we can't do anything other than to skip the document
            stream, new_hash = self.download_document(document)

            # Check if the document hash has changed
            if record and record.parsed and record.hash == new_hash:
                changed = False
            else:
                action = "updated"

        # Skip parsing if the document is unchanged
        if not changed:
            # Remove lunch schedules, snack menus and lunch menus older than 1 week from the database
            # fmt: off
            if record.effective and record.effective < datetime.datetime.now().date() - datetime.timedelta(weeks=1):
                match document.type.value:
                    case "lunch-schedule":
                        self.session.query(LunchSchedule).filter(LunchSchedule.date == record.effective).delete()
                    case "snack-menu":
                        self.session.query(SnackMenu).filter(SnackMenu.date == record.effective).delete()
                    case "lunch-menu":
                        self.session.query(LunchMenu).filter(LunchMenu.date == record.effective).delete()
            # fmt: on

            # Changed can only be false if there is an existing record
            if typing.TYPE_CHECKING:
                assert record

            if record.effective:
                self.logger.info(
                    "Skipped because the %s document for %s is unchanged",
                    document.type.value,
                    record.effective,
                )
            else:
                self.logger.info(
                    "Skipped because the %s document from %s is unchanged",
                    document.type.value,
                    record.created,
                )

            self.logger.debug("URL: %s", record.url)
            self.logger.debug("Hash: %s", record.hash)
            self.logger.debug("Created date: %s", record.created)
            self.logger.debug("Modified date: %s", record.modified)
            self.logger.debug("Effective date: %s", record.effective)

            _effective = record.effective.isoformat() if record.effective else None
            span.set_tag("document.hash", record.hash)
            span.set_tag("document.created", record.created)
            span.set_tag("document.modified", record.modified)
            span.set_tag("document.effective", _effective)
            span.set_tag("document.action", "skipped")

            return

        if parsable:
            # Get the document's effective date using subclassed method
            # If this fails, we can't do anything other than to skip the document
            effective = self.get_document_effective(document)

            # Parse the document using subclassed method and handle any errors
            # If this fails, we store the record but mark it for later parsing
            try:
                self.parse_document(document, stream, effective)
                stream.seek(0)
            except Exception as error:
                self._handle_document_error(error, document, record, created, modified, effective)
                crashed = True

        if extractable:
            # Get the document content from the subclassed method and handle any errors
            # If this fails, we store the record but mark it for later parsing
            try:
                content = self.extract_document(document, stream)
                stream.seek(0)
            except Exception as error:
                self._handle_document_error(error, document, record, created, modified, None)
                crashed = True

        # == DOCUMENT RECORD (SET)

        # Create a new document record if needed
        if not record:
            record = Document()
            record.created = created
            action = "created"

        # Update the record with new info
        if action != "skipped":
            record.title = self.get_document_title(document)
            record.url = document.url
            record.type = document.type
            record.modified = modified

            if parsable:
                record.effective = effective
                record.hash = new_hash
                record.parsed = True

            if extractable:
                record.hash = new_hash
                record.content = content
                record.parsed = True

            if crashed:
                record.parsed = False
                action = "crashed"

            self.session.add(record)

        # Update Sentry span tags with new document info
        _effective = record.effective.isoformat() if record.effective else None
        span.set_tag("document.hash", record.hash)
        span.set_tag("document.created", record.created)
        span.set_tag("document.modified", record.modified)
        span.set_tag("document.effective", _effective)
        span.set_tag("document.action", action)

        # Log the document status
        # fmt: off
        match (action, effective):
            case ("created", None):
                self.logger.info("Created a new %s document from %s", document.type.value, created)
            case ("created", effective):
                self.logger.info("Created a new %s document for %s", document.type.value, effective)

            case ("updated", None):
                self.logger.info("Updated the %s document from %s", document.type.value, created)
            case ("updated", _):
                self.logger.info("Updated the %s document for %s", document.type.value, effective)

            case ("skipped", None):
                self.logger.info("Skipped because the %s document from %s is already stored", document.type.value, created)
            case ("skipped", _):
                self.logger.info("Skipped because the %s document for %s is already stored", document.type.value, effective)
        # fmt: on

    def retrieve_document(self, document: DocumentInfo) -> Document | None:
        """Get a document record from the database. May be set by subclasses."""

        return (
            self.session.query(Document)
            .filter(Document.type == document.type, Document.url == document.url)
            .first()
        )

    @with_span(op="download")
    def download_document(self, document: DocumentInfo) -> tuple[BytesIO, str]:
        """Download a document and return its content stream and hash"""

        try:
            response = self.requests.get(self.tokenize_url(document.url))
            response.raise_for_status()

            content = response.content
            sha = sha256(content).hexdigest()
            return BytesIO(content), sha

        except OSError as error:
            raise self.error(f"Error while downloading a {document.type.value} document") from error

    def _handle_document_error(
        self,
        error: Exception,
        document: DocumentInfo,
        record: Document | None,
        created: datetime.datetime,
        modified: datetime.datetime,
        effective: datetime.date | None,
    ) -> None:
        """Set Sentry error details and logs the document error."""

        if sentry_available:
            import sentry_sdk

            # fmt: off
            sentry_sdk.set_context("document", {
                "URL": document.url,
                "source": self.source,
                "type​": document.type.value,
                "format": document.extension,
                "created": record.created if record else created,
                "modified": modified,
                "effective": effective.isoformat() if effective else None,
            })
            # fmt: on

            sentry_sdk.set_tag("document_source", self.source)
            sentry_sdk.set_tag("document_type", document.type.value)
            sentry_sdk.set_tag("document_format", document.extension)

        self.logger.exception(error)

    def normalize_url(self, url: str) -> str:
        """Return the normalized document URL. May be set by subclasses."""

        return url

    def tokenize_url(self, url: str) -> str:
        """Return the tokenized document URL. May be set by subclasses."""

        return url

    @abstractmethod
    def get_documents(self) -> Iterator[DocumentInfo]:
        """Return documents provided by the updater's source. Must be set by subclasses."""

    @abstractmethod
    def get_document_title(self, document: DocumentInfo) -> str:
        """Return the normalized document title. Must be set by subclasses."""

    @abstractmethod
    def get_document_effective(self, document: DocumentInfo) -> datetime.date:
        """Return the document effective date in a local timezone. Must be set by subclasses."""

    # noinspection PyMethodMayBeStatic
    def document_has_changed(self, document: DocumentInfo, existing: Document) -> bool:
        """Return whether the document has changed. May be set by subclasses."""

        # We treat all documents as changed by default
        # We won't reparse documents with the same hash anyway
        return True

    @abstractmethod
    def document_needs_parsing(self, document: DocumentInfo) -> bool:
        """Return whether the document needs parsing. Must be set by subclasses."""

    @abstractmethod
    def parse_document(self, document: DocumentInfo, stream: BytesIO, effective: datetime.date) -> None:
        """Parse the document and store extracted data. Must be set by subclasses."""

    @abstractmethod
    def document_needs_extraction(self, document: DocumentInfo) -> bool:
        """Return whether the document content needs to be extracted. Must be set by subclasses."""

    @abstractmethod
    def extract_document(self, document: DocumentInfo, stream: BytesIO) -> str | None:
        """Extract the document content and return it as HTML. Must be set by subclasses."""
