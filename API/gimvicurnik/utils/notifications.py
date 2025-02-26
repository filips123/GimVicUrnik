from __future__ import annotations

import enum


@enum.unique
class NotificationType(enum.Enum):
    IMMEDIATE_SUBSTITUTION = "immediate-substitution"
    SCHEDULED_SUBSTITUTION = "scheduled-substitution"
    CIRCULAR = "circular"
    LUNCH_MENU = "lunch-menu"
    SNACK_MENU = "snack-menu"


def get_page_name(type: NotificationType) -> str:
    match type:
        case NotificationType.IMMEDIATE_SUBSTITUTION | NotificationType.SCHEDULED_SUBSTITUTION:
            return "timetable"
        case NotificationType.CIRCULAR:
            return "circulars"
        case NotificationType.LUNCH_MENU | NotificationType.SNACK_MENU:
            return "menu"
