from __future__ import annotations

import typing

from .base import BaseHandler
from ..database import Notification, Session

if typing.TYPE_CHECKING:
    from typing import Any
    from flask import Blueprint
    from ..config import Config


class NotificationsHandler(BaseHandler):
    name = "notifications"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        @bp.route("/notifications")
        def get_notifications() -> list[dict[str, Any]]:
            # fmt: off
            query = (
                Session.query(
                    Notification.date,
                    Notification.title,
                    Notification.content,
                    Notification.visible
                )
                .order_by(
                    Notification.date,
                )
            )
            # fmt: on

            return [
                {
                    "date": notification.date.isoformat(),
                    "title": notification.title,
                    "content": notification.content,
                }
                for notification in query
                if notification.visible
            ]
