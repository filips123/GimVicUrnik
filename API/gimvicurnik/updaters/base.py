from __future__ import annotations

import datetime
import typing
from abc import ABC, abstractmethod
from hashlib import sha256

import attrs
import requests

from ..database import Document
from ..utils.sentry import sentry_available, with_span

if typing.TYPE_CHECKING:
    from typing import ClassVar, Iterator
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
                        "created": document.created,
                        "modified": document.modified,
                        "type​": document.type.value,
                    })
                    # fmt: on

                    sentry_sdk.set_tag("document_source", self.source)
                    sentry_sdk.set_tag("document_type", document.type.value)

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
                "type": document.type.value,
                "created​": document.created,
                "modified​": document.modified,
            },
        )

        # Populate Sentry span tags with document info
        # We set action to crashed but override it later
        span.description = document.url
        span.set_tag("document.url", document.url)
        span.set_tag("document.type", document.type.value)
        span.set_tag("document.created", document.created)
        span.set_tag("document.modified", document.modified)
        span.set_tag("document.action", "crashed")

        # == DOCUMENT RECORD (GET)

        # Try to find an existing document record
        record: Document | None = (
            self.session.query(Document)
            .filter(Document.type == document.type, Document.url == document.url)
            .first()
        )

        # == DOCUMENT PROCESSING

        # Store of value for content of circulars
        doc_content = None

        # Get the modified time if it is set, otherwise use the current time
        created = document.created or datetime.datetime.utcnow()
        modified = document.modified or created

        if self.document_needs_parsing(document):
            parsable = True
            has_content = False
            crashed = False
            action = "updated"

            # Download the document and get its content and hash
            # If this fails, we can't do anything other than to skip the document
            content, new_hash = self.download_document(document)

            # Skip parsing if the document is unchanged
            if record and record.parsed and record.hash == new_hash:
                self.logger.info(
                    "Skipped because the %s document for %s is unchanged",
                    document.type.value,
                    record.effective,
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

            # Get the document's effective date using subclassed method
            # If this fails, we can't do anything other than to skip the document
            effective = self.get_document_effective(document)

            # Parse the document using subclassed method and handle any errors
            # If this fails, we store the record but mark it for later parsing
            try:
                self.parse_document(document, content, effective)
            except Exception as error:
                if sentry_available:
                    import sentry_sdk

                    # fmt: off
                    sentry_sdk.set_context("document", {
                        "URL": document.url,
                        "created": record.created if record else created,
                        "modified": modified,
                        "effective": effective.isoformat(),
                        "type​": document.type.value,
                    })
                    # fmt: on

                    sentry_sdk.set_tag("document_source", self.source)
                    sentry_sdk.set_tag("document_type", document.type.value)

                self.logger.exception(error)
                crashed = True

        elif self.document_has_content(document):
            parsable = False
            has_content = True
            crashed = False
            action = "updated"
            effective = None

            # Download the document and get its content and hash
            # If this fails, we can't do anything other than to skip the document
            content, new_hash = self.download_document(document)

            # Skip parsing if the document is unchanged
            if record and record.parsed and record.hash == new_hash:
                self.logger.info(
                    "Skipped because the %s document from %s is unchanged",
                    document.type.value,
                    record.created,
                )

                self.logger.debug("URL: %s", record.url)
                self.logger.debug("Hash: %s", record.hash)
                self.logger.debug("Created date: %s", record.created)
                self.logger.debug("Modified date: %s", record.modified)

                span.set_tag("document.hash", record.hash)
                span.set_tag("document.created", record.created)
                span.set_tag("document.modified", record.modified)
                span.set_tag("document.action", "skipped")

                return

            # Get the document content from the subclassed method and handle any errors
            # If this fails, we store the record but mark it for later parsing
            try:
                doc_content = self.get_content(document, content)
            except Exception as error:
                if sentry_available:
                    import sentry_sdk

                    # fmt: off
                    sentry_sdk.set_context("document", {
                        "URL": document.url,
                        "created": record.created if record else created,
                        "modified": modified,
                        "type​": document.type.value,
                    })
                    # fmt: on

                    sentry_sdk.set_tag("document_source", self.source)
                    sentry_sdk.set_tag("document_type", document.type.value)

                self.logger.exception(error)
                crashed = True
            pass

        else:
            parsable = False
            has_content = False
            crashed = False
            action = "skipped"
            effective = None
            new_hash = None

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

            if has_content:
                record.hash = new_hash
                record.content = doc_content
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
        if parsable:
            if action == "created":
                self.logger.info("Created a new %s document for %s", document.type.value, effective)
            elif action == "updated":
                self.logger.info("Updated the %s document for %s", document.type.value, effective)
        elif has_content:
            if action == "created":
                self.logger.info("Created a new %s document from %s", document.type.value, created)
            elif action == "updated":
                self.logger.info("Updated the %s document from %s", document.type.value, created)
        else:
            if action == "created":
                self.logger.info("Created a new %s document", document.type.value)
            elif action == "skipped":
                self.logger.info("Skipped because the %s document is already stored", document.type.value)

    def download_document(self, document: DocumentInfo) -> tuple[bytes, str]:
        """Download a document and return its content and hash"""

        try:
            response = requests.get(self.tokenize_url(document.url))
            response.raise_for_status()

            content = response.content
            sha = sha256(content).hexdigest()
            return content, sha

        except IOError as error:
            raise self.error(f"Error while downloading a {document.type.value} document") from error

    # noinspection PyMethodMayBeStatic
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

    @abstractmethod
    def document_needs_parsing(self, document: DocumentInfo) -> bool:
        """Return whether the document needs parsing. Must be set by subclasses."""

    @abstractmethod
    def parse_document(self, document: DocumentInfo, content: bytes, effective: datetime.date) -> None:
        """Parse the document and store extracted data. Must be set by subclasses."""

    @abstractmethod
    def document_has_content(self, document: DocumentInfo) -> bool:
        """Return whether the document has content. Must be set by subclasses."""

    @abstractmethod
    def get_content(self, document: DocumentInfo, content: bytes) -> str | None:
        """Get the HTML string of content of document type circular"""
