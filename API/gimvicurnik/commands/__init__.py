import logging
import typing

import click
from flask import current_app

from ..database import Base, SessionFactory
from ..updaters import EClassroomUpdater, MenuUpdater, TimetableUpdater
from ..utils.sentry import with_transaction

if typing.TYPE_CHECKING:
    from .. import GimVicUrnik


@click.command("update-timetable", help="Update the timetable data.")
@with_transaction(name="update-timetable", op="command")
def update_timetable_command() -> None:
    """Update data from the timetable"""

    logging.getLogger(__name__).info("Updating the timetable data")

    with SessionFactory.begin() as session:
        gimvicurnik: GimVicUrnik = current_app.config["GIMVICURNIK"]
        updater = TimetableUpdater(gimvicurnik.config.sources.timetable, session)
        updater.update()


@click.command("update-eclassroom", help="Update the e-classroom data.")
@with_transaction(name="update-eclassroom", op="command")
def update_eclassroom_command() -> None:
    """Update data from the e-classroom."""

    logging.getLogger(__name__).info("Updating the e-classroom data")

    with SessionFactory.begin() as session:
        gimvicurnik: GimVicUrnik = current_app.config["GIMVICURNIK"]
        updater = EClassroomUpdater(gimvicurnik.config.sources.eclassroom, session)
        updater.update()


@click.command("update-menu", help="Update the menu data.")
@with_transaction(name="update-menu", op="command")
def update_menu_command() -> None:
    """Update snack and lunch menu data ."""

    logging.getLogger(__name__).info("Updating the menu data")

    with SessionFactory.begin() as session:
        gimvicurnik: GimVicUrnik = current_app.config["GIMVICURNIK"]
        updater = MenuUpdater(gimvicurnik.config.sources.menu, session)
        updater.update()


@click.command("create-database", help="Create the database.")
@with_transaction(name="create-database", op="command")
def create_database_command() -> None:
    """Create a new database and all tables."""

    logging.getLogger(__name__).info("Creating the database")
    gimvicurnik: GimVicUrnik = current_app.config["GIMVICURNIK"]
    Base.metadata.create_all(gimvicurnik.engine)
