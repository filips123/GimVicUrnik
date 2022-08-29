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
                Session.query(
                    Document.type,
                    Document.created,
                    Document.modified,
                    Document.effective,
                    Document.url,
                    Document.title,
                    Document.content,
                )
                .order_by(
                    Document.created,
                    Document.modified,
                )
            )
            # fmt: on

            return [
                {
                    "type": document.type.value,
                    "created": document.created.isoformat() if document.created else None,
                    "modified": document.modified.isoformat() if document.modified else None,
                    "effective": document.effective.isoformat() if document.effective else None,
                    "url": document.url,
                    "title": document.title,
                    "content": document.content,
                }
                for document in query
            ]
