from __future__ import annotations

import typing

from .base import BaseHandler
from ..database import Document, Session

if typing.TYPE_CHECKING:
    from typing import Any, Dict, List
    from flask import Blueprint
    from ..config import Config


class DocumentsHandler(BaseHandler):
    name = "documents"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        @bp.route("/documents")
        def get_documents() -> List[Dict[str, Any]]:
            # fmt: off
            query = (
                Session.query(Document.date, Document.type, Document.url, Document.description)
                .order_by(Document.date)
            )
            # fmt: on

            return [
                {
                    "date": model.date.strftime("%Y-%m-%d"),
                    "type": model.type.value,
                    "url": model.url,
                    "description": model.description,
                }
                for model in query
            ]
