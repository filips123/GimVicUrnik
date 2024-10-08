GimVičUrnik - API
=================

An API for a school timetable, substitutions and menus at Gimnazija Vič.

## Description

This is the API part of the GimVičUrnik system. For more details see [the main README file](../README.md).

## Installation

GimVičUrnik API requires Python 3.10 or later, and [Poetry](https://python-poetry.org/) dependency manager with the [`poetry-dynamic-versioning`](https://pypi.org/project/poetry-dynamic-versioning/) plugin.

You can clone this repository and install it using Poetry:

```bash
git clone https://github.com/filips123/GimVicUrnik.git
cd GimVicUrnik/API
poetry install
```

This will download and install all required dependencies and add `gimvicurnik` as command. Depending on your Poetry configuration, you might need to activate its virtual environment to use the command.

You will also need to install [one of SQLAlchemy dialects](https://docs.sqlalchemy.org/en/20/dialects/index.html) to use databases other than SQLite. The `mysql-py` (pymysql), `mysql-c` (mysqlclient) and `pgsql` (psycopg2) dialects are already specified as package extras. Optional [Sentry](https://sentry.io/) is available as a `sentry` extra.

## Usage

### Configuration

GimVičUrnik API uses YAML file for configuration. Example file can be found at [`config.yaml.sample`](config.yaml.sample). You can also see default values and the schema [in the source code](gimvicurnik/config/__init__.py). If you don't plan to use Sentry, you can delete its section entirely. Logging section will by default display INFO or higher log levels to stdout, but you can also delete or change it if you don't want that.

You need to obtain the e-classroom token as specified in the [Moodle Forum Discussion](https://moodle.org/mod/forum/discuss.php?d=193857). To run Solsis updater, you will also need Solsis API token. If you don't have one, you can use the e-classroom updater with the parse substitutions option instead, to parse substitution from PDF files.

It is recommended to set the configuration file as `GIMVICURNIK_CONFIG` environment variable, but setting `--config` argument also mostly works.

### Preparation

You need to run `gimvicurnik create-database` to create all required database tables before running other commands or the server.

### Fetching Data

Data need to be fetched and updated in separate commands from the web server. Most likely you want to execute them periodically in a cron job.

* `gimvicurnik update-timetable`: Update the timetable data
* `gimvicurnik update-eclassroom`: Update the e-classroom data (~~substitutions~~, lunch schedules, circulars)
* `gimvicurnik update-menu`: Update the menu data (snack and lunch menu)
* `gimvicurnik update-solsis`: Update the Solsis data (substitutions)

### Starting Server

The development server can be started with `gimvicurnik run`. It is based on the default Flask's built-in server and will respect all of its environment variables (except `FLASK_APP`, which is configured automatically).

In production, you should use any WSGI-compatible server. See [Flask Documentation](https://flask.palletsprojects.com/en/2.3.x/deploying/) for more details. GimVičUrnik API uses the app factory located at `gimvicurnik.create_app` to create the application.

### Using the API

You can retrieve all API routes using the `gimvicurnik routes` commands. The official client can be found [in the `website` directory](../website).

## Contributing

The API uses ruff for linting and formatting the code, and mypy for typechecking. They are included in the project's development dependencies.

Please make sure that your changes are formatted correctly according to the code style:

* Linting: `ruff check`
* Formatting: `ruff format`
* Typechecking: `mypy gimvicurnik`
