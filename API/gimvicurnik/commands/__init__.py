import datetime
import logging

import click
from flask import current_app
from flask.cli import with_appcontext

from ..database import Base, Class, Classroom, LunchMenu, LunchSchedule, SnackMenu, Substitution, Teacher
from ..updaters import EClassroomUpdater, MenuUpdater, TimetableUpdater
from ..utils.database import session_scope
from ..utils.sentry import with_transaction


@click.command("update-timetable", help="Update the timetable data.")
@with_transaction(name="update-timetable", op="command")
@with_appcontext
def update_timetable_command():
    """Update data from the timetable"""

    logging.getLogger(__name__).info("Updating the timetable data")

    with session_scope() as session:
        updater = TimetableUpdater(current_app.gimvicurnik.config["sources"]["timetable"], session)
        updater.update()


@click.command("update-eclassroom", help="Update the e-classroom data.")
@with_transaction(name="update-eclassroom", op="command")
@with_appcontext
def update_eclassroom_command():
    """Update data from the e-classroom."""

    logging.getLogger(__name__).info("Updating the e-classroom data")

    with session_scope() as session:
        updater = EClassroomUpdater(current_app.gimvicurnik.config["sources"]["eclassroom"], session)
        updater.update()


@click.command("update-menu", help="Update the menu data.")
@with_transaction(name="update-menu", op="command")
@with_appcontext
def update_menu_command():
    """Update snack and lunch menu data ."""

    logging.getLogger(__name__).info("Updating the menu data")

    with session_scope() as session:
        updater = MenuUpdater(current_app.gimvicurnik.config["sources"]["menu"], session)
        updater.update()


@click.command("create-database", help="Create the database.")
@with_transaction(name="create-database", op="command")
@with_appcontext
def create_database_command():
    """Create a new database and all tables."""

    logging.getLogger(__name__).info("Creating the database")
    Base.metadata.create_all(current_app.gimvicurnik.engine)


@click.command("cleanup-database", help="Clean up the database.")
@with_transaction(name="cleanup-database", op="command")
@with_appcontext
def cleanup_database_command():
    """Clean up the database."""

    logging.getLogger(__name__).info("Cleaning up the database")

    with session_scope() as session:
        # Remove old (> 14 days) substitutions/menus/schedules
        for entity in (Substitution, LunchSchedule, SnackMenu, LunchMenu):
            for model in session.query(entity):
                if (datetime.datetime.now().date() - model.date).days > 14:
                    logging.getLogger(__name__).info(
                        "Removing the %s from %s", model.__class__.__name__.lower(), model.date
                    )
                    session.delete(model)

        # Remove classes/teachers/classrooms without lessons/substitutions
        for entity in (Class, Teacher, Classroom):
            for model in session.query(entity):
                if len(model.lessons) == 0 and len(model.substitutions) == 0:
                    logging.getLogger(__name__).info(
                        "Removing the unused %s %s", model.__class__.__name__.lower(), model.name
                    )
                    session.delete(model)
