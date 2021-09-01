import os
from datetime import datetime, timedelta

import yaml
from flask import Flask, jsonify, render_template, request
from schema import Optional, Or, Schema, SchemaError
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import scoped_session
from werkzeug.exceptions import HTTPException

from .commands import (
    cleanup_database_command,
    create_database_command,
    create_substitutions_command,
    update_eclassroom_command,
    update_menu_command,
    update_timetable_command,
)
from .database import Class, Classroom, Document, Entity, LunchMenu, LunchSchedule, Session, SnackMenu, Teacher
from .errors import ConfigError, ConfigParseError, ConfigReadError, ConfigValidationError
from .utils.flask import DateConverter, ListConverter
from .utils.ical import create_calendar
from .utils.url import tokenize_url


class GimVicUrnik:
    """
    Main GimVicUrnik application that loads and validates the configuration
    file, configures logging, sentry and database, and registers commands
    and application routes.
    """

    schema = Schema(
        {
            "sources": {
                "timetable": {
                    "url": str,
                },
                "eclassroom": {
                    "url": str,
                    "token": str,
                    "course": int,
                    "pluginfile": {
                        "webservice": str,
                        "normal": str,
                        Optional("shareToken", default=False): bool,
                    },
                },
                "menu": {
                    "url": str,
                },
            },
            "urls": {
                "website": str,
                "api": str,
            },
            "database": str,
            Optional("sentry"): {
                "dsn": str,
                Optional("enabled", default=True): bool,
                Optional("collectIPs", default=False): bool,
                Optional("releasePrefix", default=""): str,
                Optional("releaseSuffix", default=""): str,
                Optional("maxBreadcrumbs", default=100): int,
                Optional("sampleRate", default={"commands": 0.5, "requests": 0.25, "other": 0.25}): {
                    "commands": float,
                    "requests": float,
                    "other": float,
                },
            },
            Optional("logging"): Or(dict, str),
            Optional("cors"): [str],
            "hourtimes": [
                {
                    "hour": {
                        "name": str,
                        "start": str,
                        "end": str,
                    }
                },
            ],
            Optional("debug", default=False): bool,
        }
    )

    def __init__(self, configfile):
        try:
            with open(configfile, encoding="utf-8") as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
        except OSError as error:
            raise ConfigReadError(str(error)) from error
        except yaml.YAMLError as error:
            raise ConfigParseError(str(error)) from error

        try:
            self.config = self.schema.validate(config)
        except SchemaError as error:
            raise ConfigValidationError(str(error)) from error

        self.configure_logging()
        self.configure_sentry()

        self.session: scoped_session = None  # type: ignore
        self.engine = create_engine(self.config["database"])
        Session.configure(bind=self.engine)

        self.app = Flask("gimvicurnik", static_folder=None)
        self.app.gimvicurnik = self

        self.create_sentry_hooks()
        self.create_error_hooks()
        self.create_database_hooks()
        self.create_cors_hooks()

        self.convert_date_objects()

        self.register_route_converters()
        self.register_jinja_filters()
        self.register_commands()
        self.register_routes()

    def configure_logging(self):
        """Configure logging from file or dict config if requested in the configuration file."""

        if "logging" in self.config:
            import logging.config

            if isinstance(self.config["logging"], dict):
                logging.config.dictConfig(self.config["logging"])
            elif isinstance(self.config["logging"], str):
                logging.config.fileConfig(self.config["logging"])

    def configure_sentry(self):
        """Configure Sentry integration if requested in the configuration file."""

        if "sentry" in self.config and self.config["sentry"]["enabled"]:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

            # Try to get package version, otherwise use commit hash from Sentry
            # Also modify version so it becomes valid SemVer version
            try:
                import pkg_resources

                version = pkg_resources.get_distribution("gimvicurnik").version
                version = version.replace(".", "$$$", 2).replace(".", "-", 1).replace("$$$", ".")

            except Exception:
                from sentry_sdk.utils import get_default_release

                version = get_default_release()

            environment = os.environ.get("FLASK_ENV", "production")
            release = self.config["sentry"]["releasePrefix"] + version + self.config["sentry"]["releaseSuffix"]

            # Create custom traces sampler so command and request traces can be configured separately
            def _sentry_traces_sampler(context):
                if context["transaction_context"]["op"] == "command":
                    return self.config["sentry"]["sampleRate"]["commands"]
                elif context["transaction_context"]["op"] == "http.server":
                    return self.config["sentry"]["sampleRate"]["requests"]
                else:
                    return self.config["sentry"]["sampleRate"]["other"]

            # Init the Sentry SDK
            sentry_sdk.init(
                dsn=self.config["sentry"]["dsn"],
                max_breadcrumbs=self.config["sentry"]["maxBreadcrumbs"],
                traces_sampler=_sentry_traces_sampler,
                integrations=[FlaskIntegration(transaction_style="url"), SqlalchemyIntegration()],
                environment=environment,
                release=release,
            )

    def create_sentry_hooks(self):
        """Add user IP to Sentry if this is enabled, except if user has DNT or GPC headers."""

        if "sentry" in self.config and self.config["sentry"]["collectIPs"]:
            from sentry_sdk.integrations import wsgi
            import sentry_sdk

            @self.app.before_request
            def _add_user_ip():
                # Add non-identifiable user ID to users with DNT or GPC headers
                if request.headers.get("DNT") == "1" or request.headers.get("Sec-GPC") == "1":
                    sentry_sdk.set_user({"id": "0000000000000000000000000000000000000000"})
                    return

                # Use Sentry helper to get user IP
                sentry_sdk.set_user({"ip_address": wsgi.get_client_ip(request.environ)})

    def create_error_hooks(self):
        """Add error handlers that will show errors as JSON."""

        @self.app.errorhandler(HTTPException)
        def resource_not_found(error):
            return (
                jsonify(
                    {
                        "error": {
                            "status": error.code,
                            "name": error.name,
                            "description": error.description,
                        },
                    },
                ),
                error.code,
            )

    def create_database_hooks(self):
        """Create and close the database session for each request."""

        @self.app.before_request
        def _create_session():
            self.session = scoped_session(Session)

        @self.app.teardown_request
        def _close_session(error):
            if error:
                self.session.rollback()
            else:
                self.session.commit()
                self.session.close()

    def create_cors_hooks(self):
        """Allow CORS for specific URLs."""

        @self.app.after_request
        def _apply_cors(response):
            if "cors" not in self.config:
                return response

            # Set request origin as allowed origin if it is allowed in config
            if "*" in self.config["cors"]:
                response.headers["Access-Control-Allow-Origin"] = "*"
            elif "Origin" in request.headers and request.headers["Origin"] in self.config["cors"]:
                response.headers["Access-Control-Allow-Origin"] = request.headers["Origin"]

            # Allow Sentry-Trace header
            response.headers["Access-Control-Allow-Headers"] = "Sentry-Trace"

            return response

    def convert_date_objects(self):
        """Convert %H%M notation to Python `datetime` object for all hour times."""

        for hour in self.config["hourtimes"]:
            date_start = datetime.strptime(hour["hour"]["start"], "%H%M")
            date_end = datetime.strptime(hour["hour"]["end"], "%H%M")
            hour["hour"]["start"] = timedelta(hours=date_start.hour, minutes=date_start.minute)
            hour["hour"]["end"] = timedelta(hours=date_end.hour, minutes=date_end.minute)

    def register_route_converters(self):
        """Register all custom route converters."""

        self.app.url_map.converters["date"] = DateConverter
        self.app.url_map.converters["list"] = ListConverter

    def register_jinja_filters(self):
        """Register all custom Jinja filters."""

        def format_date(date):
            return date.strftime("%d. %m. %Y")

        filters = self.app.jinja_env.filters
        filters["date_format_daily"] = format_date
        filters["date_format_weekly"] = lambda date: f"{format_date(date)} — {format_date((date + timedelta(days=4)))}"

    def register_commands(self):
        """Register all application commands."""

        self.app.cli.add_command(update_timetable_command)
        self.app.cli.add_command(update_eclassroom_command)
        self.app.cli.add_command(update_menu_command)
        self.app.cli.add_command(create_database_command)
        self.app.cli.add_command(cleanup_database_command)

        if "debug" in self.config and self.config["debug"]:
            self.app.cli.add_command(create_substitutions_command)

    def register_routes(self):
        """Register all application routes."""

        def create_feed(filter, name, type, format, display_date=None, display_date_type="daily"):
            query = (
                self.session.query(Document.date, Document.type, Document.url, Document.description)
                .filter(filter)
                .order_by(Document.date)
            )

            content = render_template(
                f"{format}.xml",
                urls=self.config["urls"],
                name=name,
                type=type,
                entries=query,
                last_updated=max(model.date for model in query),
                display_date=display_date,
                display_date_type=display_date_type,
            )

            return (
                content,
                200,
                {"Content-Type": f"application/{format}+xml; charset=utf-8"},
            )

        @self.app.route("/list/classes")
        def _list_classes():
            return jsonify([model.name for model in self.session.query(Class).order_by(Class.name)])

        @self.app.route("/list/teachers")
        def _list_teachers():
            return jsonify([model.name for model in self.session.query(Teacher).order_by(Teacher.name)])

        @self.app.route("/list/classrooms")
        def _list_classrooms():
            return jsonify([model.name for model in self.session.query(Classroom).order_by(Classroom.name)])

        @self.app.route("/timetable")
        def _get_timetable():
            return jsonify(list(Entity.get_lessons(self.session)))

        @self.app.route("/timetable/classes/<list:classes>")
        def _get_timetable_for_classes(classes):
            return jsonify(list(Class.get_lessons(self.session, classes)))

        @self.app.route("/timetable/teachers/<list:teachers>")
        def _get_timetable_for_teachers(teachers):
            return jsonify(list(Teacher.get_lessons(self.session, teachers)))

        @self.app.route("/timetable/classrooms/<list:classrooms>")
        def _get_timetable_for_classrooms(classrooms):
            return jsonify(list(Classroom.get_lessons(self.session, classrooms)))

        @self.app.route("/timetable/classrooms/empty")
        def _get_timetable_for_empty_classrooms():
            return jsonify(list(Classroom.get_empty(self.session)))

        @self.app.route("/substitutions/date/<date:date>")
        def _get_substitutions(date):
            return jsonify(list(Entity.get_substitutions(self.session, date)))

        @self.app.route("/substitutions/date/<date:date>/classes/<list:classes>")
        def _get_substitutions_for_classes(date, classes):
            return jsonify(list(Class.get_substitutions(self.session, date, classes)))

        @self.app.route("/substitutions/date/<date:date>/teachers/<list:teachers>")
        def _get_substitutions_for_teachers(date, teachers):
            return jsonify(list(Teacher.get_substitutions(self.session, date, teachers)))

        @self.app.route("/substitutions/date/<date:date>/classrooms/<list:classrooms>")
        def _get_substitutions_for_classrooms(date, classrooms):
            return jsonify(list(Classroom.get_substitutions(self.session, date, classrooms)))

        @self.app.route("/schedule/date/<date:date>")
        def _get_lunch_schedule(date):
            return jsonify(
                [
                    {
                        "class": model.class_.name,
                        "date": model.date.strftime("%Y-%m-%d"),
                        "time": model.time.strftime("%H:%M"),
                        "location": model.location,
                        "notes": model.notes,
                    }
                    for model in (
                        self.session.query(LunchSchedule)
                        .join(Class)
                        .filter(LunchSchedule.date == date)
                        .order_by(LunchSchedule.time, LunchSchedule.class_)
                    )
                ]
            )

        @self.app.route("/schedule/date/<date:date>/classes/<list:classes>")
        def _get_lunch_schedule_for_class(date, classes):
            return jsonify(
                [
                    {
                        "class": model.class_.name,
                        "date": model.date.strftime("%Y-%m-%d"),
                        "time": model.time.strftime("%H:%M"),
                        "location": model.location,
                        "notes": model.notes,
                    }
                    for model in (
                        self.session.query(LunchSchedule)
                        .join(Class)
                        .filter(LunchSchedule.date == date, Class.name.in_(classes))
                        .order_by(LunchSchedule.time, LunchSchedule.class_)
                    )
                ]
            )

        @self.app.route("/menus/date/<date:date>")
        def _get_menus(date):
            snack = self.session.query(SnackMenu).filter(SnackMenu.date == date).first()
            lunch = self.session.query(LunchMenu).filter(LunchMenu.date == date).first()

            if snack:
                snack = {
                    "normal": snack.normal,
                    "poultry": snack.poultry,
                    "vegetarian": snack.vegetarian,
                    "fruitvegetable": snack.fruitvegetable,
                }

            if lunch:
                lunch = {
                    "normal": lunch.normal,
                    "vegetarian": lunch.vegetarian,
                }

            return jsonify(
                {
                    "snack": snack,
                    "lunch": lunch,
                }
            )

        @self.app.route("/documents")
        def _get_documents():
            query = self.session.query(Document.date, Document.type, Document.url, Document.description).order_by(Document.date)

            config = self.config["sources"]["eclassroom"]["pluginfile"]
            token = self.config["sources"]["eclassroom"]["token"]

            return jsonify(
                [
                    {
                        "date": model.date.strftime("%Y-%m-%d"),
                        "type": model.type,
                        "url": model.url if not config["shareToken"] else tokenize_url(model.url, config, token),
                        "description": model.description,
                    }
                    for model in query
                ]
            )

        @self.app.route("/feeds/circulars.atom")
        def _circulars_get_atom():
            return create_feed(
                filter=or_(Document.type == "circular", Document.type == "other"),
                name="Okrožnice",
                type="circulars",
                format="atom",
                display_date=False,
            )

        @self.app.route("/feeds/circulars.rss")
        def _circulars_get_rss():
            return create_feed(
                filter=or_(Document.type == "circular", Document.type == "other"),
                name="Okrožnice",
                type="circulars",
                format="rss",
                display_date=False,
            )

        @self.app.route("/feeds/substitutions.atom")
        def _substitutions_get_atom():
            return create_feed(
                filter=Document.type == "substitutions",
                name="Nadomeščanja",
                type="substitutions",
                format="atom",
                display_date=True,
                display_date_type="daily",
            )

        @self.app.route("/feeds/substitutions.rss")
        def _substitutions_get_rss():
            return create_feed(
                filter=Document.type == "substitutions",
                name="Nadomeščanja",
                type="substitutions",
                format="rss",
                display_date=True,
                display_date_type="daily",
            )

        @self.app.route("/feeds/schedules.atom")
        def _schedules_get_atom():
            return create_feed(
                filter=Document.type == "lunch-schedule",
                name="Razporedi kosil",
                type="schedules",
                format="atom",
                display_date=True,
                display_date_type="daily",
            )

        @self.app.route("/feeds/schedules.rss")
        def _schedules_get_rss():
            return create_feed(
                filter=Document.type == "lunch-schedule",
                name="Razporedi kosil",
                type="schedules",
                format="rss",
                display_date=True,
                display_date_type="daily",
            )

        @self.app.route("/feeds/menus.atom")
        def _menu_get_atom():
            return create_feed(
                filter=or_(Document.type == "snack-menu", Document.type == "lunch-menu"),
                name="Jedilniki",
                type="menus",
                format="atom",
                display_date=True,
                display_date_type="weekly",
            )

        @self.app.route("/feeds/menus.rss")
        def _menu_get_rss():
            return create_feed(
                filter=or_(Document.type == "snack-menu", Document.type == "lunch-menu"),
                name="Jedilniki",
                type="menus",
                format="rss",
                display_date=True,
                display_date_type="weekly",
            )

        @self.app.route("/calendar/combined/<list:classes>")
        def _get_calendar_for_classes(classes):
            return create_calendar(
                Class.get_substitutions(self.session, None, classes),
                Class.get_lessons(self.session, classes),
                self.config["hourtimes"],
                f"Koledar - {', '.join(classes)} - Gimnazija Vič",
            )

        @self.app.route("/calendar/timetable/<list:classes>")
        def _get_calendar_timetable_for_classes(classes):
            return create_calendar(
                Class.get_substitutions(self.session, None, classes),
                Class.get_lessons(self.session, classes),
                self.config["hourtimes"],
                f"Urnik - {', '.join(classes)} - Gimnazija Vič",
                substitutions=False,
            )

        @self.app.route("/calendar/substitutions/<list:classes>")
        def _get_calendar_substitutions_for_classes(classes):
            return create_calendar(
                Class.get_substitutions(self.session, None, classes),
                Class.get_lessons(self.session, classes),
                self.config["hourtimes"],
                f"Nadomeščanja - {', '.join(classes)} - Gimnazija Vič",
                timetable=False,
            )


def create_app():
    """Application factory that accepts a configuration file from environment variable."""

    if "GIMVICURNIK_CONFIG" in os.environ:
        configfile = os.environ.get("GIMVICURNIK_CONFIG")
    else:
        raise ConfigError("Missing config filename")

    gimvicurnik = GimVicUrnik(configfile)
    return gimvicurnik.app
