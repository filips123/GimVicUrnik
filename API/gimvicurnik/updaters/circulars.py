from __future__ import annotations

import datetime
import logging
import os
import re
import typing
from collections import defaultdict
from email.utils import parsedate_to_datetime
from pathlib import PurePosixPath
from urllib.parse import urljoin, urlparse, urlunparse
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, ParserRejectedMarkup

from .base import BaseMultiUpdater, DocumentInfo
from ..database import DocumentType
from ..errors import CircularsApiError, InvalidIdentifierError
from ..errors import OrphanedAttachmentError
from ..utils.docx import extract_content
from ..utils.sentry import sentry_available
from ..utils.sentry import with_span

if typing.TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
    from io import BytesIO
    from sqlalchemy.orm import Session
    from sentry_sdk.tracing import Span
    from ..config import ConfigSourcesCirculars


class CircularsUpdater(BaseMultiUpdater):
    source = "circulars"
    error = CircularsApiError

    def __init__(self, config: ConfigSourcesCirculars, session: Session):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.session = session

        super().__init__()

        self.circulars: dict[str, str] = {}

    def get_documents(self) -> Iterator[DocumentInfo]:
        yield from self._get_documents_from_circulars()
        yield from self._get_documents_from_attachments()

    @staticmethod
    def _extract_identifier(filename: str) -> str | None:
        """Extract and normalize circular identifier from a filename."""

        if match := re.match(r"^(\d+)[-_](\d+)[-_]", filename):
            return f"{match.group(1)}-{match.group(2)}"

        return None

    def _enrich_sentry_context(self, url: str, doctype: DocumentType, extension: str) -> None:
        """Enrich Sentry context with document information in case of errors."""

        if sentry_available:
            import sentry_sdk

            # fmt: off
            sentry_sdk.set_context("document", {
                "URL": url,
                "source": self.source,
                "type​": doctype.value,
                "format": extension,
            })
            # fmt: on

            sentry_sdk.set_tag("document_source", self.source)
            sentry_sdk.set_tag("document_type", doctype.value)
            sentry_sdk.set_tag("document_format", extension)

    def _get_documents_from_circulars(self) -> Iterator[DocumentInfo]:
        """Download and parse the main listing and get circulars."""

        doctype = DocumentType.CIRCULAR

        try:
            params = {"psk": self.config.token}
            response = self.client.get(self.config.circularsUrl).query(params).build().send()
            content = response.text()
        except OSError as error:
            raise CircularsApiError("Error while downloading circulars listing") from error

        try:
            soup = with_span(op="soup")(BeautifulSoup)(content, features="lxml")
        except ParserRejectedMarkup as error:
            raise CircularsApiError("Error while parsing circulars listing") from error

        for circular in soup.select("ul li a[href]"):
            title = circular.get_text(strip=True)

            url = circular["href"]
            assert isinstance(url, str)

            # All circulars are also provided in DOCX, but PDF may be linked in the listing
            parsed = urlparse(url)
            path = PurePosixPath(parsed.path).with_suffix(".docx")
            extension = path.suffix[1:]
            url = urlunparse(parsed._replace(path=str(path)))

            identifier = self._extract_identifier(path.stem)

            if not identifier:
                self._enrich_sentry_context(url, doctype, extension)
                error = InvalidIdentifierError("Unknown circular identifier: " + url.rsplit("/", 1)[1])
                self.logger.error(error)
                continue

            # Store circular titles so they can be used for attachments later
            self.circulars[identifier] = title

            yield DocumentInfo(type=doctype, title=title, url=url, extension=extension)

    def _get_documents_from_attachments(self) -> Iterator[DocumentInfo]:
        """Download and parse the attachment listing and get attachments."""

        doctype = DocumentType.OTHER

        tz = ZoneInfo(self.config.timezone)

        try:
            response = self.client.get(self.config.attachmentsUrl).build().send()
            content = response.text()
        except OSError as error:
            raise CircularsApiError("Error while downloading attachments listing") from error

        try:
            soup = with_span(op="soup")(BeautifulSoup)(content, features="lxml")
        except ParserRejectedMarkup as error:
            raise CircularsApiError("Error while parsing attachments listing") from error

        attachments: defaultdict[str, list[DocumentInfo]] = defaultdict(list)

        for row in soup.find_all("tr"):
            cells = row.find_all("td")

            # Skip parent directory row
            if len(cells) < 3 or not cells[1].text.strip() or not cells[2].text.strip():
                continue

            url = urljoin(self.config.attachmentsUrl, cells[1].find("a")["href"])
            path = urlparse(url).path
            extension = os.path.splitext(path)[1][1:]

            date = datetime.datetime.strptime(cells[2].text.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=tz)

            identifier = self._extract_identifier(os.path.basename(path))

            if not identifier:
                self._enrich_sentry_context(url, doctype, extension)
                error = InvalidIdentifierError("Unknown attachment identifier: " + url.rsplit("/", 1)[1])
                self.logger.error(error)
                continue

            if identifier not in self.circulars:
                self._enrich_sentry_context(url, doctype, extension)
                error = OrphanedAttachmentError("Attachment without circular: " + url.rsplit("/", 1)[1])
                self.logger.error(error)
                continue

            attachments[identifier].append(
                DocumentInfo(
                    type=doctype,
                    url=url,
                    modified=date,
                    extension=extension,
                )
            )

        for identifier, documents in attachments.items():
            title = self.circulars[identifier]

            for index, document in enumerate(documents, start=1):
                suffix = f" {index}" if len(documents) > 1 else ""
                document.title = f"{title} \u2013 Priponka{suffix}"
                yield document

    def get_document_title(self, document: DocumentInfo) -> str:
        """Return the normalized document title."""

        assert document.title
        return document.title

    def get_document_effective(self, document: DocumentInfo) -> None:
        """Return the document effective date in a local timezone from the URL."""

        # Circulars have no effective date
        return None

    def get_document_created(
        self,
        document: DocumentInfo,
        stream: BytesIO,
        headers: Mapping[str, str],
    ) -> datetime.datetime | None:
        """Return the document created date."""

        # If document info do not have created date, rely on base updater fallback
        return (
            document.created.replace(second=0, microsecond=0).astimezone(datetime.timezone.utc)
            if document.created
            else None
        )

    def get_document_modified(
        self,
        document: DocumentInfo,
        stream: BytesIO,
        headers: Mapping[str, str],
    ) -> datetime.datetime | None:
        """Return the document modified date."""

        # If document info do not have modified date, try to get it from the headers
        return (
            (document.modified or parsedate_to_datetime(headers["Last-Modified"]))
            .replace(second=0, microsecond=0)
            .astimezone(datetime.timezone.utc)
        )

    def document_needs_download(self, document: DocumentInfo) -> bool:
        """Return whether the document must be downloaded."""

        # We need to download the document to get the modified date
        return not document.modified

    def document_needs_parsing(self, document: DocumentInfo) -> bool:
        """Return whether the document needs parsing."""

        # Circulars have nothing to parse
        return False

    def parse_document(self, document: DocumentInfo, stream: BytesIO, effective: datetime.date) -> None:
        """Parse the document and store extracted data."""

        # Circulars have nothing to parse
        return None

    def document_needs_extraction(self, document: DocumentInfo) -> bool:
        """Return whether the document content needs to be extracted."""

        # Only DOCX documents (circulars and some other) can have content extracted
        if document.extension == "docx":
            return True

        return False

    @with_span(op="content", pass_span=True)
    def extract_document(self, document: DocumentInfo, content: BytesIO, span: Span) -> str | None:  # type: ignore[override]
        """Extract the document content and return it as HTML."""

        span.set_tag("document.source", self.source)
        span.set_tag("document.type", document.type.value)
        span.set_tag("document.format", document.extension)

        # Convert DOCX to HTML
        return extract_content(content)
