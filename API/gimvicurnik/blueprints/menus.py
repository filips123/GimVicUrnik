from __future__ import annotations

import typing

from .base import BaseHandler
from ..database import LunchMenu, Session, SnackMenu

if typing.TYPE_CHECKING:
    import datetime
    from typing import Any
    from flask import Blueprint
    from ..config import Config


class MenusHandler(BaseHandler):
    name = "menus"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        @bp.route("/menus/date/<date:date>")
        def get_menus(date: datetime.date) -> dict[str, dict[str, str] | None]:
            # We need type "any" here, otherwise mypy complains
            # See: https://github.com/python/mypy/issues/15101
            snack: Any = Session.query(SnackMenu).filter(SnackMenu.date == date).first()
            lunch: Any = Session.query(LunchMenu).filter(LunchMenu.date == date).first()

            if snack:
                snack = {
                    "normal": snack.normal,
                    "poultry": snack.poultry,
                    "vegetarian": snack.vegetarian,
                    "fruitvegetable": snack.fruitvegetable,
                }

            if lunch:
                lunch = {
                    "until": lunch.until.strftime("%H:%M") if lunch.until else None,
                    "normal": lunch.normal,
                    "vegetarian": lunch.vegetarian,
                }

            return {
                "snack": snack,
                "lunch": lunch,
            }
