from __future__ import annotations

import os
import traceback
import typing

import click
from flask.cli import FlaskGroup, ScriptInfo

from .errors import ConfigError

if typing.TYPE_CHECKING:
    from typing import List


class GimVicUrnikGroup(FlaskGroup):
    """
    Special subclass of the :class:`flask.cli.FlaskGroup` group that
    supports setting configuration file as a command argument and modifies
    the help text.
    """

    def __init__(self) -> None:
        def _set_config_filename(ctx: click.Context, _param: str, value: str) -> None:
            """Set configuration file from argument."""

            if not value or ctx.resilient_parsing:
                return

            os.environ["GIMVICURNIK_CONFIG"] = value

        def _get_version(ctx: click.Context, _param: str, value: str) -> None:
            """Display version information for all important packages."""

            if not value or ctx.resilient_parsing:
                return

            from importlib import metadata
            import platform

            python_version = platform.python_version()
            gimvicurnik_version = metadata.version("gimvicurnik")
            sqlalchemy_version = metadata.version("sqlalchemy")
            requests_version = metadata.version("requests")
            flask_version = metadata.version("flask")
            werkzeug_version = metadata.version("werkzeug")
            pymupdf_version = metadata.version("pymupdf")
            pdf2docx_version = metadata.version("pdf2docx")
            openpyxl_version = metadata.version("openpyxl")

            try:
                sentry_version = metadata.version("sentry-sdk")
            except metadata.PackageNotFoundError:
                sentry_version = "None"

            click.echo(
                f"Python: {python_version}\n"
                f"GimVicUrnik: {gimvicurnik_version}\n"
                f"SQLAlchemy: {sqlalchemy_version}\n"
                f"Requests: {requests_version}\n"
                f"Flask: {flask_version}\n"
                f"Werkzeug: {werkzeug_version}\n"
                f"PyMuPDF: {pymupdf_version}\n"
                f"pdf2docx: {pdf2docx_version}\n"
                f"openpyxl: {openpyxl_version}\n"
                f"Sentry SDK: {sentry_version}",
                color=ctx.color,
            )
            ctx.exit()

        params = [
            click.Option(
                ["--config"],
                help="Set a config file name.",
                metavar="filename",
                type=str,
                callback=_set_config_filename,
            ),
            click.Option(
                ["--version"],
                help="Show the GimVicUrnik version and exit.",
                expose_value=False,
                callback=_get_version,
                is_flag=True,
                is_eager=True,
            ),
        ]

        help = (
            "A utility script for the GimVicUrnik application.\n\n"
            "Configuration file can be provided as --config argument or as the "
            "GIMVICURNIK_CONFIG environment variable. Development mode can be "
            "enabled with the FLASK_ENV environment variable set to 'development'.\n\n"
            "Note: Due to the limitations of the command parser, some application-specific "
            "commands won't be displayed in the command list if the configuration file "
            "is not specified as environment variable or is invalid."
        )

        # Use custom version option to print other relevant versions
        super().__init__(add_version_option=False, params=params, help=help)

    def main(self) -> None:  # type: ignore[override]
        """Set the Flask app and start the main command handler."""

        os.environ["FLASK_APP"] = "gimvicurnik"
        super().main()

    def list_commands(self, ctx: click.Context) -> List[str]:
        """Prevent crashing on config errors when showing list of commands or help."""

        self._load_plugin_commands()

        rv = set(super(FlaskGroup, self).list_commands(ctx))
        info = ctx.ensure_object(ScriptInfo)

        try:
            rv.update(info.load_app().cli.list_commands(ctx))
        except ConfigError as error:
            click.secho(f"Error: {error}\n", err=True, fg="red")
        except Exception:
            click.secho(f"{traceback.format_exc()}\n", err=True, fg="red")

        return sorted(rv)


def main() -> None:
    cli = GimVicUrnikGroup()
    cli.main()


if __name__ == "__main__":
    main()
