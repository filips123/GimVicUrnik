import logging
import typing

import click
from flask import current_app

from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from ..database import Base, SessionFactory, Document, DocumentType
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


@click.command("cleanup-database", help="Clean up the database.")
@with_transaction(name="cleanup-database", op="command")
def cleanup_database_command() -> None:
    """Remove lunch schedules, snack menus and lunch menus older than 2 weeks from the database."""

    logging.getLogger(__name__).info("Cleaning up the database")

    with SessionFactory.begin() as session:
        session.query(Document).filter(
            and_(
                or_(
                    Document.type == DocumentType.LUNCH_SCHEDULE,
                    Document.type == DocumentType.SNACK_MENU,
                    Document.type == DocumentType.LUNCH_MENU,
                ),
                Document.effective < datetime.now().date() - timedelta(weeks=2),
            )
        ).delete()


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
