from __future__ import annotations

import datetime
import logging
import os
import re
import tempfile
import typing

import requests
from bs4 import BeautifulSoup, ParserRejectedMarkup
from openpyxl import load_workbook
from pdf2docx import extract_tables  # type: ignore

from .base import BaseMultiUpdater, DocumentInfo
from ..database import DocumentType, LunchMenu, SnackMenu
from ..errors import MenuApiError, MenuDateError, MenuFormatError
from ..utils.sentry import with_span

if typing.TYPE_CHECKING:
    from typing import Iterator, Optional
    from sqlalchemy.orm import Session
    from sentry_sdk.tracing import Span
    from ..config import ConfigSourcesMenu


class MenuUpdater(BaseMultiUpdater):
    source = "website"
    error = MenuApiError

    def __init__(self, config: ConfigSourcesMenu, session: Session):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.session = session

    def get_documents(self) -> Iterator[DocumentInfo]:
        """Download and parse the website to retrieve all menu URLs."""

        try:
            response = requests.get(self.config.url)
            response.raise_for_status()

            soup = with_span(op="soup")(BeautifulSoup)(response.text, features="lxml")
        except (IOError, ParserRejectedMarkup) as error:
            raise MenuApiError("Error while downloading or parsing menu index") from error

        menus = soup.find_all("li", {"class": "jedilnik"})
        if not menus:
            self.logger.info("No menus found")
            return iter(())

        for menu in menus:
            for link in menu.find_all("a", href=True):
                contents = str(link.contents[0]).lower()

                if "malica" in contents:
                    menu_type = DocumentType.SNACK_MENU
                elif "kosilo" in contents:
                    menu_type = DocumentType.LUNCH_MENU
                else:
                    continue

                menu_url = self.config.url + link["href"]
                yield DocumentInfo(type=menu_type, url=menu_url)

    def get_document_title(self, document: DocumentInfo) -> str:
        """Return the document name from its type."""

        if document.type == DocumentType.SNACK_MENU:
            return "Jedilnik za malico"
        elif document.type == DocumentType.LUNCH_MENU:
            return "Jedilnik za kosilo"
        else:
            # This cannot happen because only menus are provided by the API
            raise KeyError("Unknown document type for menu")

    def get_document_effective(self, document: DocumentInfo) -> datetime.date:
        """Parse and return custom date formats from the document URL."""

        short_month_to_number = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "maj": 5,
            "jun": 6,
            "jul": 7,
            "avg": 8,
            "sep": 9,
            "okt": 10,
            "nov": 11,
            "dec": 12,
        }

        long_month_to_number = {
            "januar": 1,
            "februar": 2,
            "marec": 3,
            "april": 4,
            "maj": 5,
            "junij": 6,
            "julij": 7,
            "avgust": 8,
            "september": 9,
            "oktober": 10,
            "november": 11,
            "december": 12,
        }

        url = document.url

        # Some empty strings are needed here because of a Black bug that removed our comments
        # TODO: Remove them once the project updates to Black 22.7 (or a version with the fix)
        # SEE: https://github.com/psf/black/issues/2646

        # == FORMAT TYPE 1
        # Example: KOSILO-4jan-8jan-2021.pdf
        # Example: KOSILO-25jan-29jan-2021-PDF.pdf
        ""
        date = re.search(r"(?:KOSILO|MALICA)-(\d+)([a-z]+)-\d+[a-z]+-(\d+)(?i:-PDF)?\.[a-z]+", url)  # fmt: skip

        if date:
            return datetime.date(
                year=int(date.group(3)),
                month=short_month_to_number[date.group(2)],
                day=int(date.group(1)),
            )

        # == FORMAT TYPE 2
        # Example: 09-splet-oktober-1-teden-09-M.pdf
        # Example: 05-splet-februar-3-teden-M-PDF.pdf
        # Example: 04-splet-marec-2-teden-04-M-PDF-0.pdf
        # Example: 01-splet-september-4-teden-02-M-popravek.pdf
        # Example: 01-splet-januar1-teden-02-K.pdf
        # Example: 01-splet-september-2-teden-02.pdf
        # Example: 01-splet-september-2-teden-M-02.pdf
        ""
        date = re.search(r"\d+-splet-([a-z]+)-?(\d)-teden(?:-[MK])?-?\d*(?:-[MK])?-?\d?(?i:-PDF)?(?:-[a-z]+)?(?:-\d)?\.[a-z]+", url)  # fmt: skip

        if date:
            today = datetime.date.today()
            year = today.year

            # Get week and month from URL
            week = int(date.group(2))
            month = long_month_to_number[date.group(1)]

            # In case the menu is provided for the next year
            if today.month == 12 and month == 1:
                year += 1

            # In case the menu is provided for the last year
            if today.month == 1 and month == 12:
                year -= 1

            # Get start of nth week of the month
            first = datetime.date(year, month, 1)
            diff = -first.weekday() if month == 9 else 7 - first.weekday()
            diff = diff if diff < 7 else 0
            new = first + datetime.timedelta(weeks=week - 1, days=diff)

            return new

        # == UNKNOWN FORMAT
        raise MenuDateError("Unknown menu date URL format: " + url.rsplit("/", 1)[-1])

    def document_needs_parsing(self, document: DocumentInfo) -> bool:
        """Return whether the document needs parsing."""

        # All documents provided by this updater need parsing
        return True

    @with_span(op="parse", pass_span=True)
    def parse_document(self, document: DocumentInfo, content: bytes, effective: datetime.date, span: Span) -> None:  # type: ignore[override]
        """Parse the document and store extracted data."""

        # Get document format from its URL
        docformat = document.url.rsplit(".", 1)[-1]
        span.set_tag("document.format", docformat)
        span.set_tag("document.type", document.type.value)

        # Save the content to a temporary file
        filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex() + ".pdf")
        file = open(filename, mode="w+b")
        file.write(content)
        file.close()

        if document.type == DocumentType.SNACK_MENU:
            self._parse_snack_menu(docformat, filename, effective)
        elif document.type == DocumentType.LUNCH_MENU:
            self._parse_lunch_menu(docformat, filename, effective)
        else:
            # This cannot happen because only menus are provided by the API
            raise KeyError("Unknown document type for menu")

    def _parse_snack_menu(self, docformat: str, filename: str, effective: datetime.date) -> None:
        """Parse the snack menu document."""

        if docformat == "pdf":
            # Extract all tables from a PDF file
            tables = with_span(op="extract")(extract_tables)(filename)
            os.remove(filename)

            days = 0

            # Parse tables into menus and store them
            for table in tables:
                for row in table:
                    if len(row) != 5 or "NV in N" in row[1]:
                        continue

                    current = effective + datetime.timedelta(days=days)
                    days += 1

                    menu = {
                        "date": current,
                        "normal": row[1],
                        "poultry": row[2],
                        "vegetarian": row[3],
                        "fruitvegetable": row[4],
                    }

                    model = self.session.query(SnackMenu).filter(SnackMenu.date == current).first()

                    if not model:
                        model = SnackMenu()

                    for key in menu:
                        setattr(model, key, menu[key])

                    self.session.add(model)

        elif docformat == "xlsx":
            # Extract workbook from an XLSX file
            wb = with_span(op="extract")(load_workbook)(filename, read_only=True, data_only=True)

            menu = {}
            days = 0

            # Parse tables into menus and store them
            for ws in wb:
                for wr in ws.iter_rows(min_row=1, max_col=3):
                    if not hasattr(wr[0].border, "bottom"):
                        continue

                    # Store the menu after the end of table
                    if wr[0].border.bottom.color:
                        if menu and menu["date"]:
                            # fmt: off
                            model = (
                                self.session.query(SnackMenu)
                                .filter(SnackMenu.date == menu["date"])
                                .first()
                            )
                            # fmt: on

                            if not model:
                                model = SnackMenu()

                            model.date = menu["date"]
                            model.normal = "\n".join(menu["normal"][1:])
                            model.poultry = "\n".join(menu["poultry"][1:])
                            model.vegetarian = "\n".join(menu["vegetarian"][1:])
                            model.fruitvegetable = "\n".join(menu["fruitvegetable"][1:])

                            self.session.add(model)
                            days += 1

                        menu = {
                            "date": None,
                            "normal": [],
                            "poultry": [],
                            "vegetarian": [],
                            "fruitvegetable": [],
                        }

                    if wr[0].value and isinstance(wr[0].value, datetime.datetime):
                        menu["date"] = effective + datetime.timedelta(days=days)

                    if wr[1].value:
                        menu["normal"].append(wr[1].value.strip())

                    if wr[2].value:
                        menu["poultry"].append(wr[2].value.strip())

                    if wr[3].value:
                        menu["vegetarian"].append(wr[3].value.strip())

                    if wr[4].value:
                        menu["fruitvegetable"].append(wr[4].value.strip())

            wb.close()
            os.remove(filename)

        else:
            raise MenuFormatError("Unknown snack menu document format: " + docformat)

    def _parse_lunch_menu(self, docformat: str, filename: str, effective: datetime.date) -> None:
        """Parse the lunch menu document."""

        if docformat == "pdf":
            # Extract all tables from a PDF file
            tables = with_span(op="extract")(extract_tables)(filename)
            os.remove(filename)

            days = 0

            # Parse tables into menus and store them
            for table in tables:
                for row in table:
                    if len(row) != 3 or "N KOSILO" in row[1]:
                        continue

                    current = effective + datetime.timedelta(days=days)
                    days += 1

                    menu = {
                        "date": current,
                        "normal": row[1],
                        "vegetarian": row[2],
                    }

                    model = self.session.query(LunchMenu).filter(LunchMenu.date == current).first()

                    if not model:
                        model = LunchMenu()

                    for key in menu:
                        setattr(model, key, menu[key])

                    self.session.add(model)

        elif format == "xlsx":
            # Extract workbook from an XLSX file
            wb = with_span(op="extract")(load_workbook)(filename, read_only=True, data_only=True)

            menu = {}
            days = 0

            # Parse tables into menus and store them
            for ws in wb:
                for wr in ws.iter_rows(min_row=1, max_col=3):
                    if not hasattr(wr[0].border, "bottom"):
                        continue

                    if wr[0].border.bottom.color:
                        if menu and menu["date"]:
                            # fmt: off
                            model = (
                                self.session.query(LunchMenu)
                                .filter(LunchMenu.date == menu["date"])
                                .first()
                            )
                            # fmt: on

                            if not model:
                                model = LunchMenu()

                            model.date = menu["date"]
                            model.normal = "\n".join(menu["normal"][1:])
                            model.vegetarian = "\n".join(menu["vegetarian"][1:])

                            self.session.add(model)
                            days += 1

                        menu = {
                            "date": None,
                            "normal": [],
                            "vegetarian": [],
                        }

                    if wr[0].value and isinstance(wr[0].value, datetime.datetime):
                        menu["date"] = effective + datetime.timedelta(days=days)

                    if wr[1].value:
                        menu["normal"].append(wr[1].value.strip())

                    if wr[2].value:
                        menu["vegetarian"].append(wr[2].value.strip())

            wb.close()
            os.remove(filename)

        else:
            raise MenuFormatError("Unknown lunch menu document format: " + docformat)

    def document_has_content(self, document: DocumentInfo) -> bool:
        """Menu documents do not have content."""

        return False

    def get_content(self, document: DocumentInfo, content: bytes) -> Optional[str]:
        """Menu documents do not have content."""

        return None
