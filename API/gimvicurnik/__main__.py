import os
import sys

import click
from flask.cli import FlaskGroup, ScriptInfo

from .errors import ConfigError


class GimVicUrnikGroup(FlaskGroup):
    """
    Special subclass of the :class:`~flask.cli.FlaskGroup` group that
    supports setting configuration file as a command argument and modifies
    the help text.
    """

    def __init__(self):
        def _set_config_filename(ctx, param, value):
            """Set configuration file from argument."""

            if value:
                os.environ["GIMVICURNIK_CONFIG"] = value

        def _get_version(ctx, param, value):
            if not value or ctx.resilient_parsing:
                return

            import pkg_resources
            import platform

            python_version = platform.python_version()
            gimvicurnik_version = pkg_resources.get_distribution("gimvicurnik").version
            sqlalchemy_version = pkg_resources.get_distribution("sqlalchemy").version
            requests_version = pkg_resources.get_distribution("requests").version
            flask_version = pkg_resources.get_distribution("flask").version
            pdf2docx_version = pkg_resources.get_distribution("pdf2docx").version
            openpyxl_version = pkg_resources.get_distribution("openpyxl").version

            try:
                sentry_version = pkg_resources.get_distribution("sentry-sdk").version
            except pkg_resources.DistributionNotFound:
                sentry_version = "None"

            click.echo(
                f"Python: {python_version}\n"
                f"GimVicUrnik: {gimvicurnik_version}\n"
                f"SQLAlchemy: {sqlalchemy_version}\n"
                f"Requests: {requests_version}\n"
                f"Flask: {flask_version}\n"
                f"pdf2docx: {pdf2docx_version}\n"
                f"openpyxl: {openpyxl_version}\n"
                f"Sentry SDK: {sentry_version}"
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
            "enabled with the FLASK_ENV environment variable to 'development'.\n\n"
            "Note: Due to the limitations of the command parser, some application-specific "
            "commands won't be displayed in the command list if the configuration file "
            "is not specified as environment variable or is invalid."
        )

        # Use custom version option to display arguments in correct order and add other relevant versions
        super().__init__(add_version_option=False, params=params, help=help)

    def main(self, as_module=False):
        """Set a Flask app and start the main command handler."""

        os.environ["FLASK_APP"] = "gimvicurnik"
        super().main(args=sys.argv[1:], prog_name="python -m gimvicurnik" if as_module else None)


def main(as_module=False):
    def _list_commands(self, ctx):
        self._load_plugin_commands()

        rv = set(super(FlaskGroup, self).list_commands(ctx))
        info = ctx.ensure_object(ScriptInfo)

        try:
            rv.update(info.load_app().cli.list_commands(ctx))
        except ConfigError as error:
            click.secho(f"Error: {error}", err=True, fg="red")

        return sorted(rv)

    # Monkey-patch Flask's list_commands to hide any config errors when showing list of commands or help
    FlaskGroup.list_commands = _list_commands

    # Run GimVicUrnik's command group
    cli = GimVicUrnikGroup()
    cli.main(as_module)


if __name__ == "__main__":
    main(as_module=True)
