GimVičUrnik
===========

An API for a school timetable, substitutions and menus at Gimnazija Vič.

## Description

This is the API part of the GimVičUrnik system. For more details see [the main README file](../README.md).

## Installation

GimVičUrnik API requires Python 3.6 or later and [Poetry](https://python-poetry.org/) dependency manager. You may also need to install [`poetry-dynamic-versioning`](https://pypi.org/project/poetry-dynamic-versioning/).

You can then clone this repository and install it using Poetry:

```bash
git clone https://github.com/filips123/GimVicUrnik.git
cd GimVicUrnik/API
poetry install
```

This will download and install all required dependencies and add `gimvicurnik` as command. Note that depending on your Poetry configuration, you might need to activate its virtual environment to use the command.

You will also need to install [one of SQLAlchemy dialects](https://docs.sqlalchemy.org/en/13/dialects/index.html) to use databases other than SQLite. If you want to enable optional [Sentry](https://sentry.io/) integration, you will also have to install `sentry` extra.

## Usage

### Configuration

GimVičUrnik API uses YAML file for configuration. Example file can be found at [`config.yaml.sample`](config.yaml.sample). You can also see the default values and the schema [in the source code](gimvicurnik/__init__.py). If you don't plan to use Sentry, you can delete its section entirely. Logging section will by default display INFO or higher log levels to stdout, but you can also delete or change the section if you don't want that.

You can obtain the e-classroom token as specified in the [Moodle Forum Discussion](https://moodle.org/mod/forum/discuss.php?d=193857).

It is recommended to set the configuration file as `GIMVICURNIK_CONFIG` environment variable, but setting `--config` argument also mostly works.

### Preparation

You will first need to run `gimvicurnik create-database` to create all required database tables.

### Fetching data

Data need to be fetched and updated in separate commands from the web server. Most likely you will want to execute them in cron.

* `gimvicurnik update-timetable`: Update the timetable data
* `gimvicurnik update-eclassroom`: Update the e-classroom data (substitutions, lunch schedule, circulars)
* `gimvicurnik update-menu`: Update the menu data (snack and lunch menu)
* `gimvicurnik cleanup-database`: Clean up the database (remove data older than 14 days and entities without lessons)

### Starting server

The development server can be started with `gimvicurnik run`. It is based on the default Flask's built-in server and will respect all of its environment variables (except `FLASK_APP` which is configured automatically).

You can also use any other WSGI-compatible server. See [Flask Documentation](https://flask.palletsprojects.com/en/1.1.x/deploying/) for more details. GimVičUrnik API uses app factory located at `gimvicurnik.create_app` to create the application.

### Using the API

You can retrieve all API routes using the `gimvicurnik routes` commands. The official client can be found in [in the `website` directory](../website).

##
If, at the end of the file `debug: true` flag is present, there is another command added
`gimvicurnik create-substitutions n`: Creates n random substitutions in next 14 days
## Contributing

The API uses FlakeHell and Blake for linting the code. They are included in project's development dependencies.

Please make sure that your changes are formatted correctly according to the code style:

* Linting: `flakehell lint`
* Formatting: `black gimvicurnik`
