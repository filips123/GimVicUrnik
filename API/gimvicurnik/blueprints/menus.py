from __future__ import annotations

import typing

from .base import BaseHandler
from ..database import LunchMenu, Session, SnackMenu
from ..utils.dates import get_weekdays

if typing.TYPE_CHECKING:
    import datetime
    from flask import Blueprint
    from ..config import Config


class MenusHandler(BaseHandler):
    name = "menus"

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        def _serialize_snack_menu(snack: SnackMenu) -> dict[str, str | None]:
            return {
                "normal": snack.normal,
                "poultry": snack.poultry,
                "vegetarian": snack.vegetarian,
                "fruitvegetable": snack.fruitvegetable,
            }

        def _serialize_lunch_menu(lunch: LunchMenu) -> dict[str, str | None]:
            return {
                "until": lunch.until.isoformat("minutes") if lunch.until else None,
                "normal": lunch.normal,
                "vegetarian": lunch.vegetarian,
            }

        @bp.route("/menus/date/<date:date>")
        def get_date_menus(date: datetime.date) -> dict[str, str | dict[str, str | None] | None]:
            snack = Session.query(SnackMenu).filter(SnackMenu.date == date).first()
            lunch = Session.query(LunchMenu).filter(LunchMenu.date == date).first()

            return {
                "date": date.isoformat(),
                "snack": _serialize_snack_menu(snack) if snack else None,
                "lunch": _serialize_lunch_menu(lunch) if lunch else None,
            }

        @bp.route("/menus/week/<date:date>")
        def get_week_menus(date: datetime.date) -> list[dict[str, str | dict[str, str | None] | None]]:
            weekdays = get_weekdays(date)

            snacks = Session.query(SnackMenu).filter(SnackMenu.date.in_(weekdays)).all()
            lunches = Session.query(LunchMenu).filter(LunchMenu.date.in_(weekdays)).all()

            snacks = {snack.date: _serialize_snack_menu(snack) for snack in snacks}
            lunches = {lunch.date: _serialize_lunch_menu(lunch) for lunch in lunches}

            return [
                {
                    "date": date.isoformat(),
                    "snack": snacks.get(date),
                    "lunch": lunches.get(date),
                }
                for date in weekdays
            ]
