import datetime
import hashlib
import logging
import os
import re
import tempfile

import requests
from bs4 import BeautifulSoup, ParserRejectedMarkup
from openpyxl import load_workbook
from pdf2docx import extract_tables

from ..database import Document, LunchMenu, SnackMenu
from ..errors import MenuApiError, MenuDateError, MenuFormatError
from ..utils.sentry import with_span


class MenuUpdater:
    def __init__(self, config, session):
        self.url = config["url"]
        self.session = session
        self.logger = logging.getLogger(__name__)

    def update(self):
        for type, url, date in self._get_documents():
            if type == "snack":
                self._store_snack_menu(url, date)
            elif type == "lunch":
                self._store_lunch_menu(url, date)

    def _get_documents(self):
        try:
            response = requests.get(self.url)
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
                    menu_type = "snack"
                elif "kosilo" in contents:
                    menu_type = "lunch"
                else:
                    continue

                menu_url = self.url + link["href"]
                menu_date = self._get_date(menu_url)

                yield menu_type, menu_url, menu_date

    @staticmethod
    def _get_date(url):
        # There are multiple known date formats in URLs
        # They need to be parsed separately

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

        full_month_to_number = {
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

        # Example: KOSILO-4jan-8jan-2021.pdf
        # Another example: KOSILO-25jan-29jan-2021-PDF.pdf
        date = re.search(r"(?:KOSILO|MALICA)-(\d+)([a-z]+)-\d+[a-z]+-(\d+)(?i:-PDF)?\.[a-z]+", url)

        if date:
            return datetime.date(
                year=int(date.group(3)), month=short_month_to_number[date.group(2)], day=int(date.group(1))
            )

        # Example: 09-splet-oktober-1-teden-09-M.pdf
        # Another example: 05-splet-februar-3-teden-M-PDF.pdf
        # Another example: 04-splet-marec-2-teden-04-M-PDF-0.pdf
        date = re.search(r"\d+-splet-([a-z]+)-(\d)-teden-?\d*-[MK]-?\d?(?i:-PDF)?(?:-\d)?\.[a-z]+", url)

        if date:
            year = datetime.datetime.now().year
            month = full_month_to_number[date.group(1)]

            # In case if menu is provided for the next year
            if datetime.datetime.now().month == 12 and month == 1:
                year += 1

            # In case if menu is provided for the last year
            if datetime.datetime.now().month == 1 and month == 12:
                year -= 1

            week = int(date.group(2))

            # Get start of nth week of month
            first = datetime.date(year, month, 1)
            diff = -first.weekday() if month == 9 else 7 - first.weekday()
            diff = diff if diff < 7 else 0
            new = first + datetime.timedelta(weeks=week - 1, days=diff)

            return new

        raise MenuDateError("Unknown menu date URL format: " + url.rsplit("/", 1)[-1])

    @with_span(op="document", pass_span=True)
    def _store_snack_menu(self, url, date, span):
        response = requests.get(url)
        format = url.rsplit(".", 1)[-1]

        content = response.content
        hash = str(hashlib.sha256(content).hexdigest())

        span.description = url
        span.set_tag("document.url", url)
        span.set_tag("document.type", "snack-menu")
        span.set_tag("document.format", format)

        # Skip unchanged lunch menu documents
        document = self.session.query(Document).filter(Document.type == "snack-menu", Document.url == url).first()
        if hash == getattr(document, "hash", False):
            self.logger.info("Skipped because the snack menu document for %s is unchanged", document.date)
            self.logger.debug("URL: %s", document.url)
            self.logger.debug("Date: %s", document.date)
            self.logger.debug("Hash: %s", document.hash)

            span.set_tag("document.date", document.date)
            span.set_tag("document.hash", document.hash)
            span.set_tag("document.action", "skipped")

            return

        # Save content to temporary file
        filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex() + ".pdf")
        file = open(filename, mode="w+b")
        file.write(content)
        file.close()

        if format == "pdf":
            # Extract all tables from PDF file
            tables = with_span(op="extract")(extract_tables)(filename)
            os.remove(filename)

            days = 0

            # Parse tables into menus and store them
            for table in tables:
                for row in table[1::2]:
                    current = date + datetime.timedelta(days=days)
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

        elif format == "xlsx":
            # Extract workbook from XLSX file
            wb = with_span(op="extract")(load_workbook)(filename, read_only=True, data_only=True)

            menu = None
            days = 0

            # Parse tables into menus and store them
            for ws in wb:
                for wr in ws.iter_rows(min_row=1, max_col=3):
                    if not hasattr(wr[0].border, "bottom"):
                        continue

                    if wr[0].border.bottom.color:
                        if menu and menu["date"]:
                            model = self.session.query(LunchMenu).filter(LunchMenu.date == menu["date"]).first()
                            if not model:
                                model = LunchMenu()

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
                        menu["date"] = date + datetime.timedelta(days=days)

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
            raise MenuFormatError("Unknown menu document format: " + format)

        # Update or create a document
        if not document:
            document = Document()
            created = True
        else:
            created = False

        document.date = date
        document.type = "snack-menu"
        document.url = url
        document.description = "Jedilnik za malico"
        document.hash = hash

        self.session.add(document)

        span.set_tag("document.date", document.date)
        span.set_tag("document.hash", document.hash)
        span.set_tag("document.action", "created" if created else "updated")

        if created:
            self.logger.info("Created a new snack menu document for %s", document.date)
        else:
            self.logger.info("Updated the snack menu document for %s", document.date)

    @with_span(op="document", pass_span=True)
    def _store_lunch_menu(self, url, date, span):
        response = requests.get(url)
        format = url.rsplit(".", 1)[-1]

        content = response.content
        hash = str(hashlib.sha256(content).hexdigest())

        span.description = url
        span.set_tag("document.url", url)
        span.set_tag("document.type", "lunch-menu")
        span.set_tag("document.format", format)

        # Skip unchanged lunch menu documents
        document = self.session.query(Document).filter(Document.type == "lunch-menu", Document.url == url).first()
        if hash == getattr(document, "hash", False):
            self.logger.info("Skipped because the lunch menu document for %s is unchanged", document.date)
            self.logger.debug("URL: %s", document.url)
            self.logger.debug("Date: %s", document.date)
            self.logger.debug("Hash: %s", document.hash)

            span.set_tag("document.date", document.date)
            span.set_tag("document.hash", document.hash)
            span.set_tag("document.action", "skipped")

            return

        # Save content to temporary file
        filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex() + "." + format)
        file = open(filename, mode="w+b")
        file.write(content)
        file.close()

        if format == "pdf":
            # Extract all tables from PDF file
            tables = with_span(op="extract")(extract_tables)(filename)
            os.remove(filename)

            days = 0

            # Parse tables into menus and store them
            for table in tables:
                for row in table[1::2]:
                    current = date + datetime.timedelta(days=days)
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
            # Extract workbook from XLSX file
            wb = with_span(op="extract")(load_workbook)(filename, read_only=True, data_only=True)

            menu = None
            days = 0

            # Parse tables into menus and store them
            for ws in wb:
                for wr in ws.iter_rows(min_row=1, max_col=3):
                    if not hasattr(wr[0].border, "bottom"):
                        continue

                    if wr[0].border.bottom.color:
                        if menu and menu["date"]:
                            model = self.session.query(LunchMenu).filter(LunchMenu.date == menu["date"]).first()
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
                        menu["date"] = date + datetime.timedelta(days=days)

                    if wr[1].value:
                        menu["normal"].append(wr[1].value.strip())

                    if wr[2].value:
                        menu["vegetarian"].append(wr[2].value.strip())

            wb.close()
            os.remove(filename)

        else:
            raise MenuFormatError("Unknown menu document format: " + format)

        # Update or create a document
        if not document:
            document = Document()
            created = True
        else:
            created = False

        document.date = date
        document.type = "lunch-menu"
        document.url = url
        document.description = "Jedilnik za kosilo"
        document.hash = hash

        self.session.add(document)

        span.set_tag("document.date", document.date)
        span.set_tag("document.hash", document.hash)
        span.set_tag("document.action", "created" if created else "updated")

        if created:
            self.logger.info("Created a new lunch menu document for %s", document.date)
        else:
            self.logger.info("Updated the lunch menu document for %s", document.date)
