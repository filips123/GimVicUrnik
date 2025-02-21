from __future__ import annotations

import logging
import typing
import requests
import json

from sqlalchemy import and_
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from ..database import DocumentType, Document

if typing.TYPE_CHECKING:
    from typing import Any
    from ..config import ConfigFirebase
    from sqlalchemy.orm import Session


class PushNotificationsHandler:
    def __init__(self, config: ConfigFirebase, session: Session) -> None:
        self.logger = logging.getLogger("notifications")
        self.config = config
        self.session = session

        self.credentials = credentials.Certificate("firebasecredentials.json")
        firebase_admin.initialize_app(self.credentials)

    def _get_user_tokens(self, field: str) -> list[str]:
        db = firestore.client()

        users = db.collection("users").where(filter=FieldFilter(field, "==", True)).stream()

        return [user.id for user in users]

    def _get_documents_data(self, type: DocumentType) -> list[dict[str, Any]]:
        # Filter specified documents that are not older than 15 min
        query = (
            self.session.query(Document)
            .filter(
                and_(
                    Document.type == type,
                    Document.created > datetime.now().date() - timedelta(minutes=15),
                )
            )
            .order_by(Document.created)
        )

        # Return only the useful data
        match type:
            case DocumentType.CIRCULAR:
                return [
                    {
                        "title": circular.title,
                    }
                    for circular in query
                    if circular.title
                ]
            case DocumentType.SNACK_MENU | DocumentType.LUNCH_MENU:
                return [
                    {
                        "start": menu.effective.strftime("%d. %m. %Y"),
                        "end": (menu.effective + timedelta(days=4)).strftime("%d. %m. %Y"),
                    }
                    for menu in query
                    if menu.effective
                ]

        return []

    def _send_message(self, token: str, title: str, body: str) -> None:
        url = f"https://fcm.googleapis.com/v1/projects/{self.config.projectId}/messages:send"

        message = {
            "message": {"token": token, "notification": {"title": title, "body": body}},
        }

        access_token = self.credentials.get_access_token().access_token

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        # TODO: Handle when message could not be received (probably a lost user)
        requests.post(url, headers=headers, data=json.dumps(message))

    def send_immediate_substitutions_notifications(self) -> None:
        pass

    def send_scheduled_substitutions_notifications(self) -> None:
        pass

    def send_circulars_notifications(self) -> None:
        tokens = self._get_user_tokens("circularsNotificationsEnabled")
        circulars = self._get_documents_data(DocumentType.CIRCULAR)

        for token in tokens:
            for circular in circulars:
                self._send_message(token, "Nova okrožnica", f'{circular["title"]}')

    def send_menu_notifications(self) -> None:
        tokens = self._get_user_tokens("snackMenuNotificationsEnabled")
        snack_menus = self._get_documents_data(DocumentType.SNACK_MENU)
        lunch_menus = self._get_documents_data(DocumentType.LUNCH_MENU)

        for token in tokens:
            for menu in snack_menus:
                self._send_message(token, "Jedilnik za malico", f'{menu["start"]} - {menu["end"]}')

            for menu in lunch_menus:
                self._send_message(token, "Jedilnik za kosilo", f'{menu["start"]} - {menu["end"]}')
