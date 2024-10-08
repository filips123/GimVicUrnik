from __future__ import annotations

import enum
import re
import typing
from datetime import date

from flask import render_template
from sqlalchemy import func, or_

from .base import BaseHandler
from ..database import Document, DocumentType, Session

if typing.TYPE_CHECKING:
    from typing import Any
    from flask import Blueprint
    from ..config import Config


class FeedFormat(enum.Enum):
    ATOM = "atom"
    RSS = "rss"


class FeedType(enum.Enum):
    CIRCULARS = "circulars"
    SUBSTITUTIONS = "substitutions"
    SCHEDULES = "schedules"
    MENUS = "menus"


class DateDisplay(enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


def get_mime_type(url: str) -> str:
    """Get MIME type for a few extensions we know documents use."""

    if re.search(r"\.pdf(?:\?[\w=]*)?$", url):
        return "application/pdf"
    if url.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if url.endswith(".xlsx"):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return "application/octet-stream"


class FeedHandler(BaseHandler):
    name = "feed"
    template_folder = "templates"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        def _create_feed(
            query_filter: Any,
            feed_name: str,
            feed_type: FeedType,
            feed_format: FeedFormat,
            date_display: DateDisplay = DateDisplay.NONE,
        ) -> tuple[str, int, dict[str, str]]:
            """Generate a feed from template for all documents that match the filter."""

            # Get all documents that match the filter
            query = list(
                Session.query(
                    Document.type,
                    Document.created,
                    Document.modified,
                    Document.effective,
                    Document.url,
                    Document.title,
                    Document.content,
                )
                .filter(query_filter)
                .order_by(Document.created, Document.modified)
            )

            # Find the latest feed modification datetime
            last_updated = Session.query(func.max(Document.modified)).filter(query_filter).scalar()
            last_updated = last_updated or date.fromtimestamp(0)

            # Get the frontend page based on the feed type
            feed_page = "circulars" if feed_type == FeedType.CIRCULARS else "sources"

            # Render the feed from Atom/RSS template
            content = render_template(
                f"{feed_format.value}.xml",
                urls=config.urls,
                name=feed_name,
                type=feed_type.value,
                page=feed_page,
                entries=query,
                last_updated=last_updated,
                date_display=date_display,
                get_mime_type=get_mime_type,
                DateDisplay=DateDisplay,
            )

            return content, 200, {"Content-Type": f"application/{feed_format}+xml; charset=utf-8"}

        @bp.route("/feed/circulars.atom", defaults={"feed_format": FeedFormat.ATOM})
        @bp.route("/feed/circulars.rss", defaults={"feed_format": FeedFormat.RSS})
        def get_circulars_feed(feed_format: FeedFormat) -> tuple[str, int, dict[str, str]]:
            return _create_feed(
                query_filter=or_(
                    Document.type == DocumentType.CIRCULAR,
                    Document.type == DocumentType.OTHER,
                ),
                feed_name="Okrožnice",
                feed_type=FeedType.CIRCULARS,
                feed_format=feed_format,
            )

        @bp.route("/feed/substitutions.atom", defaults={"feed_format": FeedFormat.ATOM})
        @bp.route("/feed/substitutions.rss", defaults={"feed_format": FeedFormat.RSS})
        def get_substitutions_feed(feed_format: FeedFormat) -> tuple[str, int, dict[str, str]]:
            return _create_feed(
                query_filter=Document.type == DocumentType.SUBSTITUTIONS,
                feed_name="Nadomeščanja",
                feed_type=FeedType.SUBSTITUTIONS,
                feed_format=feed_format,
                date_display=DateDisplay.DAILY,
            )

        @bp.route("/feed/schedules.atom", defaults={"feed_format": FeedFormat.ATOM})
        @bp.route("/feed/schedules.rss", defaults={"feed_format": FeedFormat.RSS})
        def get_schedules_feed(feed_format: FeedFormat) -> tuple[str, int, dict[str, str]]:
            return _create_feed(
                query_filter=Document.type == DocumentType.LUNCH_SCHEDULE,
                feed_name="Razporedi kosila",
                feed_type=FeedType.SCHEDULES,
                feed_format=feed_format,
                date_display=DateDisplay.DAILY,
            )

        @bp.route("/feed/menus.atom", defaults={"feed_format": FeedFormat.ATOM})
        @bp.route("/feed/menus.rss", defaults={"feed_format": FeedFormat.RSS})
        def get_menus_feed(feed_format: FeedFormat) -> tuple[str, int, dict[str, str]]:
            return _create_feed(
                query_filter=or_(
                    Document.type == DocumentType.SNACK_MENU,
                    Document.type == DocumentType.LUNCH_MENU,
                ),
                feed_name="Jedilniki",
                feed_type=FeedType.MENUS,
                feed_format=feed_format,
                date_display=DateDisplay.WEEKLY,
            )
