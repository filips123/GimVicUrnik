from __future__ import annotations

import datetime
import os
import typing

import cattrs
import yaml
from flask import Flask, request
from sqlalchemy import create_engine
from werkzeug.exceptions import HTTPException

from .blueprints import (
    CalendarHandler,
    DocumentsHandler,
    FeedHandler,
    ListHandler,
    MenusHandler,
    ScheduleHandler,
    SubstitutionsHandler,
    TimetableHandler,
)
from .commands import (
    cleanup_database_command,
    create_database_command,
    update_eclassroom_command,
    update_menu_command,
    update_timetable_command,
)
from .config import Config
from .database import Session, SessionFactory
from .errors import ConfigError, ConfigParseError, ConfigReadError, ConfigValidationError
from .utils.errors import format_exception
from .utils.flask import DateConverter, ListConverter

if typing.TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union
    from sqlalchemy.engine import Engine
    from werkzeug import Response
    from flask.typing import ResponseReturnValue


class GimVicUrnik:
    """
    Main GimVicUrnik application that loads and validates the configuration
    file, configures logging, sentry and database, and registers commands
    and application routes.
    """

    app: Flask
    config: Config
    engine: Engine

    def __init__(self, configfile: str) -> None:
        try:
            with open(configfile, encoding="utf-8") as file:
                config = yaml.load(file, Loader=yaml.CLoader)
                self.config = cattrs.structure(config, Config)
        except OSError as error:
            raise ConfigReadError(str(error)) from error
        except yaml.YAMLError as error:
            raise ConfigParseError(str(error)) from error
        except cattrs.errors.BaseValidationError as error:
            msg = "Failed to validate config\n" + format_exception(error)
            raise ConfigValidationError(msg) from error

        self.configure_logging()
        self.configure_sentry()
        self.configure_database()

        self.app = Flask("gimvicurnik", static_folder=None, template_folder=None)
        self.app.config["GIMVICURNIK"] = self

        self.create_error_hooks()
        self.create_sentry_hooks()
        self.create_database_hooks()
        self.create_cors_hooks()

        self.register_route_converters()
        self.register_jinja_filters()
        self.register_commands()
        self.register_routes()

    def configure_logging(self) -> None:
        """Configure logging from file or dict config."""

        if self.config.logging:
            import logging.config

            if isinstance(self.config.logging, dict):
                logging.config.dictConfig(self.config.logging)
            elif isinstance(self.config.logging, str):
                logging.config.fileConfig(self.config.logging)

    def configure_sentry(self) -> None:
        """Configure Sentry integration."""

        if self.config.sentry and self.config.sentry.enabled:
            import pkg_resources
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.pure_eval import PureEvalIntegration

            sentry_config = self.config.sentry

            # Get the package version and modify it, so it becomes valid SemVer version
            version = pkg_resources.get_distribution("gimvicurnik").version
            version = version.replace(".", "$$$", 2).replace(".", "-", 1).replace("$$$", ".")

            # Get current environment and calculate release
            environment = os.environ.get("FLASK_ENV", "production")
            release = sentry_config.releasePrefix + version + sentry_config.releaseSuffix

            # Create custom traces sampler so different traces can be configured separately
            def _sentry_traces_sampler(context: Dict[str, Any]) -> Union[float, int, bool]:
                if context["transaction_context"]["op"] == "command":
                    return sentry_config.sampleRate.commands
                elif context["transaction_context"]["op"] == "http.server":
                    return sentry_config.sampleRate.requests
                else:
                    return sentry_config.sampleRate.other

            # Init the Sentry SDK
            sentry_sdk.init(
                dsn=sentry_config.dsn,
                max_breadcrumbs=sentry_config.maxBreadcrumbs,
                traces_sampler=_sentry_traces_sampler,
                integrations=[
                    FlaskIntegration(transaction_style="url"),
                    SqlalchemyIntegration(),
                    PureEvalIntegration(),
                ],
                environment=environment,
                release=release,
            )

    def configure_database(self) -> None:
        """Configure database session."""

        self.engine = create_engine(self.config.database)
        SessionFactory.configure(bind=self.engine)

    def create_error_hooks(self) -> None:
        """Add error handlers that shows errors as JSON."""

        @self.app.errorhandler(HTTPException)
        def _handle_http_exception(error: HTTPException) -> ResponseReturnValue:
            return (
                {
                    "error": {
                        "status": error.code,
                        "name": error.name,
                        "description": error.description,
                    },
                },
                error.code or 500,
            )

    def create_sentry_hooks(self) -> None:
        """Add user's IP to Sentry if this is enabled, except if the user has DNT or GPC headers."""

        if self.config.sentry and self.config.sentry.enabled and self.config.sentry.collectIPs:
            from sentry_sdk.integrations import wsgi
            import sentry_sdk

            @self.app.before_request
            def _add_user_ip() -> None:
                # Add non-identifiable user ID to users with DNT or GPC headers
                if request.headers.get("DNT") == "1" or request.headers.get("Sec-GPC") == "1":
                    sentry_sdk.set_user({"id": "0000000000000000000000000000000000000000"})
                    return

                # Use Sentry helper to get user IP
                sentry_sdk.set_user({"ip_address": wsgi.get_client_ip(request.environ)})

    def create_database_hooks(self) -> None:
        """Remove database session after request."""

        @self.app.teardown_appcontext
        def _close_session(_error: Optional[BaseException] = None) -> None:
            Session.remove()

    def create_cors_hooks(self) -> None:
        """Allow CORS for specific URLs."""

        @self.app.after_request
        def _apply_cors(response: Response) -> Response:
            if not self.config.cors:
                return response

            # Set request origin as allowed origin if it is allowed in config
            if "*" in self.config.cors:
                response.headers["Access-Control-Allow-Origin"] = "*"
            elif "Origin" in request.headers and request.headers["Origin"] in self.config.cors:
                response.headers["Access-Control-Allow-Origin"] = request.headers["Origin"]

            # Allow Sentry-Trace and other tracing headers
            tracing_headers = "Sentry-Trace, Traceparent, Tracestate, Baggage"
            response.headers["Access-Control-Allow-Headers"] = tracing_headers

            return response

    def register_route_converters(self) -> None:
        """Register all custom route converters."""

        self.app.url_map.converters["date"] = DateConverter
        self.app.url_map.converters["list"] = ListConverter

    def register_jinja_filters(self) -> None:
        """Register all custom Jinja filters."""

        def _format_date(date: datetime.date) -> str:
            return date.strftime("%d. %m. %Y")

        def _format_week(date: datetime.date) -> str:
            return f"{_format_date(date)} — {_format_date((date + datetime.timedelta(days=4)))}"

        filters = self.app.jinja_env.filters
        filters["date"] = _format_date
        filters["week"] = _format_week

    def register_commands(self) -> None:
        """Register all application commands."""

        self.app.cli.add_command(update_timetable_command)
        self.app.cli.add_command(update_eclassroom_command)
        self.app.cli.add_command(update_menu_command)
        self.app.cli.add_command(create_database_command)
        self.app.cli.add_command(cleanup_database_command)

    def register_routes(self) -> None:
        """Register all application routes."""

        ListHandler.register(self.app, self.config)
        TimetableHandler.register(self.app, self.config)
        SubstitutionsHandler.register(self.app, self.config)
        MenusHandler.register(self.app, self.config)
        ScheduleHandler.register(self.app, self.config)
        DocumentsHandler.register(self.app, self.config)
        FeedHandler.register(self.app, self.config)
        CalendarHandler.register(self.app, self.config)


def create_app() -> Flask:
    """Application factory that accepts a configuration file from environment variable."""

    if "GIMVICURNIK_CONFIG" in os.environ:
        configfile = os.environ["GIMVICURNIK_CONFIG"]
    else:
        raise ConfigError("Missing config filename")

    gimvicurnik = GimVicUrnik(configfile)
    return gimvicurnik.app
