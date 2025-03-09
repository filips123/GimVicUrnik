from __future__ import annotations

import logging
import typing
import requests
import json
from datetime import datetime, timedelta

from sqlalchemy import and_

import firebase_admin  # type: ignore
from firebase_admin import credentials, firestore
from google.cloud.firestore import FieldFilter, And  # type: ignore

from ..database import DocumentType, Document
from ..errors import NotificationsFirestoreError
from ..utils.notifications import NotificationType, get_page_name
from ..utils.sentry import sentry_available

if typing.TYPE_CHECKING:
    from typing import Any
    from ..config import ConfigFirebase, ConfigURLs
    from sqlalchemy.orm import Session


class PushNotificationsHandler:
    def __init__(self, config_firebase: ConfigFirebase, config_urls: ConfigURLs, session: Session) -> None:
        self.logger = logging.getLogger("notifications")
        self.requests = requests.Session()
        self.config_firebase = config_firebase
        self.config_urls = config_urls
        self.session = session

        self.credentials = credentials.Certificate("firebasecredentials.json")
        firebase_admin.initialize_app(self.credentials)

        self.db = firestore.client()

    def _get_user_tokens(self, field: str) -> list[str]:
        try:
            users = self.db.collection("users").where(filter=FieldFilter(field, "==", True)).stream()
        except Exception as error:
            raise NotificationsFirestoreError("Error while filtering users collection") from error

        return [user.id for user in users]

    def _get_documents_data(self, type: DocumentType, time_span: int) -> list[dict[str, Any]]:
        # Filter specified documents that are not older than the specified time
        query = (
            self.session.query(Document)
            .filter(
                and_(
                    Document.type == type,
                    Document.created > datetime.now().date() - timedelta(minutes=time_span),
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

    def _send_message(self, type: NotificationType, token: str, title: str, body: str) -> None:
        url = f"https://fcm.googleapis.com/v1/projects/{self.config_firebase.projectId}/messages:send"

        message = {
            "message": {
                "token": token,
                "data": {
                    "title": title,
                    "body": body,
                    "link_url": self.config_urls.website + get_page_name(type),
                },
            }
        }

        access_token = self.credentials.get_access_token().access_token

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        response_json = self.requests.post(url, headers=headers, data=json.dumps(message)).json()

        if "error" in response_json:
            match response_json["error"]["code"]:
                case 404:
                    # UNREGISTERED
                    # This usually means that the token used is no longer valid, so we can delete it

                    self.db.collection("users").document(token).delete()
                case 400:
                    # INVALID_ARGUMENT
                    # Request parameters were invalid

                    if sentry_available:
                        import sentry_sdk

                        # fmt: off
                        sentry_sdk.set_context("notification", {
                            "token": token,
                            "title": title,
                            "body": body,
                        })
                        # fmt: on

                        sentry_sdk.set_tag("notification_type", type.value)

                    self.logger.info("FCM request parameters were invalid")

    def send_immediate_substitutions_notifications(self) -> None:
        pass

    def send_scheduled_substitutions_notifications(self) -> None:
        pass

    def send_circulars_notifications(self) -> None:
        tokens = self._get_user_tokens("circularsNotificationsEnabled")
        circulars = self._get_documents_data(DocumentType.CIRCULAR, 15)

        for token in tokens:
            for circular in circulars:
                self._send_message(NotificationType.CIRCULAR, token, "Nova okrožnica", f'{circular["title"]}')

    def send_menu_notifications(self) -> None:
        tokens = self._get_user_tokens("snackMenuNotificationsEnabled")
        snack_menus = self._get_documents_data(DocumentType.SNACK_MENU, 15)
        lunch_menus = self._get_documents_data(DocumentType.LUNCH_MENU, 15)

        for token in tokens:
            for menu in snack_menus:
                self._send_message(
                    NotificationType.SNACK_MENU,
                    token,
                    "Jedilnik za malico",
                    f'{menu["start"]} - {menu["end"]}',
                )

            for menu in lunch_menus:
                self._send_message(
                    NotificationType.LUNCH_MENU,
                    token,
                    "Jedilnik za kosilo",
                    f'{menu["start"]} - {menu["end"]}',
                )

    def cleanup_users(self) -> None:
        try:
            # Users that do not have any notifications enabled are probably stale
            users = (
                self.db.collection("users")
                .where(
                    filter=And(
                        [
                            FieldFilter("immediateSubstitutionsNotificationsEnabled", "==", False),
                            FieldFilter("scheduledSubstitutionsNotificationsEnabled", "==", False),
                            FieldFilter("circularsNotificationsEnabled", "==", False),
                            FieldFilter("snackMenuNotificationsEnabled", "==", False),
                            FieldFilter("lunchMenuNotificationsEnabled", "==", False),
                        ]
                    )
                )
                .stream()
            )
        except Exception as error:
            raise NotificationsFirestoreError("Error while filtering users collection") from error

        for user in users:
            self.db.collection("users").document(user.id).delete()
            self.logger.info("Deleted user from firestore:", user.id)
