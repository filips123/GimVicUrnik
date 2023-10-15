import logging
import typing

import click
from flask import current_app

from ..database import Base, SessionFactory
from ..updaters import EClassroomUpdater, TimetableUpdater
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


@click.command("create-database", help="Create the database.")
@click.option("--recreate", help="Remove existing tables before creating new ones.", is_flag=True)
@click.pass_context
def create_database_command(ctx: click.Context, recreate: bool) -> None:
    """Create a new database and all tables."""

    gimvicurnik: GimVicUrnik = current_app.config["GIMVICURNIK"]

    if recreate:
        confirm = input("Do you really want to drop the database? This cannot be reverted! [y/N]: ")

        if confirm.lower() == "y":
            logging.getLogger(__name__).info("Dropping the database")
            Base.metadata.drop_all(gimvicurnik.engine)
        else:
            ctx.abort()

    logging.getLogger(__name__).info("Creating the database")
    Base.metadata.create_all(gimvicurnik.engine)
