import logging
import typing

import click
from flask import current_app

from datetime import datetime, timedelta
from sqlalchemy import and_, or_

from ..database import Base, SessionFactory, Document, DocumentType
from ..updaters import EClassroomUpdater, MenuUpdater, TimetableUpdater, SolsisUpdater
from ..notifications import PushNotificationsHandler
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


# fmt: off

@click.command("update-eclassroom", help="Update the e-classroom data.")
@click.option("--parse-substitutions/--no-parse-substitutions", "-s/-no-s", help="Parse substitutions.", default=False)
@click.option("--parse-lunch-schedules/--no-parse-lunch-schedules", "-l/-no-l", help="Parse lunch schedules.", default=True)
@click.option("--extract-circulars/--no-extract-circulars", "-c/-no-c", help="Extract circulars.", default=True)
@with_transaction(name="update-eclassroom", op="command")
def update_eclassroom_command(parse_substitutions: bool, parse_lunch_schedules: bool, extract_circulars: bool) -> None:
    """Update data from the e-classroom."""

    logging.getLogger(__name__).info("Updating the e-classroom data")

    with SessionFactory.begin() as session:
        gimvicurnik: GimVicUrnik = current_app.config["GIMVICURNIK"]
        updater = EClassroomUpdater(gimvicurnik.config.sources.eclassroom, session, parse_substitutions, parse_lunch_schedules, extract_circulars)
        updater.update()

# fmt: on


@click.command("update-menu", help="Update the menu data.")
@with_transaction(name="update-menu", op="command")
def update_menu_command() -> None:
    """Update snack and lunch menu data ."""

    logging.getLogger(__name__).info("Updating the menu data")

    with SessionFactory.begin() as session:
        gimvicurnik: GimVicUrnik = current_app.config["GIMVICURNIK"]
        updater = MenuUpdater(gimvicurnik.config.sources.menu, session)
        updater.update()


@click.command("update-solsis", help="Update the Solsis data.")
@click.option("--date-span", "-s", nargs=2, type=str, help="Start and end date to get substitutions for.")
@with_transaction(name="update-solsis", op="command")
def update_solsis_command(date_span: tuple[str, str]) -> None:
    """Update data from Solsis."""

    # The default span is 7 days inclusive
    date_from = datetime.now().date()
    date_to = date_from + timedelta(days=6)

    if date_span:
        date_from = datetime.strptime(date_span[0], "%Y-%m-%d").date()
        date_to = datetime.strptime(date_span[1], "%Y-%m-%d").date()

    logging.getLogger(__name__).info("Updating the Solsis data (%s - %s)", date_from, date_to)

    with SessionFactory.begin() as session:
        gimvicurnik: GimVicUrnik = current_app.config["GIMVICURNIK"]
        updater = SolsisUpdater(gimvicurnik.config.sources.solsis, session, date_from, date_to)
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


@click.command("handle-notifications", help="Handle the notifications.")
@click.option("--immediate-substitutions", help="Send immediate substitutions.", is_flag=True)
@click.option("--scheduled-substitutions", help="Send scheduled substitutions.", is_flag=True)
@click.option("--circulars", help="Send circulars.", is_flag=True)
@click.option("--menus", help="Send menus.", is_flag=True)
@with_transaction(name="handle-notifications", op="command")
def handle_notifications_command(
    immediate_substitutions: bool, scheduled_substitutions: bool, circulars: bool, menus: bool
) -> None:
    """Handle the notifications."""

    logging.getLogger(__name__).info("Handling notifications")

    with SessionFactory.begin() as session:
        gimvicurnik: GimVicUrnik = current_app.config["GIMVICURNIK"]

        notifications = PushNotificationsHandler(gimvicurnik.config.firebase, session)

        if not any([immediate_substitutions, scheduled_substitutions, circulars, menus]):
            notifications.send_immediate_substitutions_notifications()
            notifications.send_scheduled_substitutions_notifications()
            notifications.send_circulars_notifications()
            notifications.send_menu_notifications()
        else:
            if immediate_substitutions:
                notifications.send_immediate_substitutions_notifications()
            if scheduled_substitutions:
                notifications.send_scheduled_substitutions_notifications()
            if circulars:
                notifications.send_circulars_notifications()
            if menus:
                notifications.send_menu_notifications()
