import os

import yaml
from flask import Flask, request, jsonify
from schema import Schema, SchemaError, Optional, Or
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session

from .commands import update_eclassroom_command, update_timetable_command, create_database_command, cleanup_database_command
from .database import Session, Document, Class, Teacher, Classroom
from .errors import ConfigError, ConfigReadError, ConfigParseError, ConfigValidationError


class GimVicUrnik:
    """
    Main GimVicUrnik application that loads and validates the configuration
    file, configures logging, sentry and database, and registers commands
    and application routes.
    """

    schema = Schema({
        'sources': {
            'timetable': {
                'url': str,
            },
            'eclassroom': {
                'url': str,
                'token': str,
                'course': int,
                Optional('restricted'): [str],
            },
        },
        'database': str,
        Optional('sentry'): {
            'dsn': str,
            Optional('enabled', default=True): bool,
            Optional('traces', default=1.0): float,
            Optional('breadcrumbs', default=100): int,
        },
        Optional('logging'): Or(dict, str),
        Optional('cors'): [str],
    })

    def __init__(self, configfile):
        try:
            with open(configfile, encoding='utf-8') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
        except OSError as error:
            raise ConfigReadError(str(error))
        except yaml.YAMLError as error:
            raise ConfigParseError(str(error))

        try:
            self.config = self.schema.validate(config)
        except SchemaError as error:
            raise ConfigValidationError(str(error))

        self.configure_logging()
        self.configure_sentry()

        self.engine = create_engine(self.config['database'])
        Session.configure(bind=self.engine)

        self.session = None

        self.app = Flask('gimvicurnik')
        self.app.gimvicurnik = self

        self.register_commands()
        self.register_routes()

        self.create_database_hooks()
        self.create_cors_hooks()

    def configure_logging(self):
        """Configure logging from file or dict config if requested in the configuration file."""

        if 'logging' in self.config:
            import logging.config

            if isinstance(self.config['logging'], dict):
                logging.config.dictConfig(self.config['logging'])
            elif isinstance(self.config['logging'], str):
                logging.config.fileConfig(self.config['logging'])

    def configure_sentry(self):
        """Configure Sentry integration if requested in the configuration file."""

        if 'sentry' in self.config and self.config['sentry']['enabled']:
            import sentry_sdk

            sentry_sdk.init(
                dsn=self.config['sentry']['dsn'],
                integrations=[FlaskIntegration(transaction_style='url'), SqlalchemyIntegration()],
                traces_sample_rate=self.config['sentry']['traces'],
                max_breadcrumbs=self.config['sentry']['breadcrumbs']
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
            if 'cors' not in self.config:
                return response

            if '*' in self.config['cors']:
                response.headers['Access-Control-Allow-Origin'] = '*'
            elif 'Origin' in request.headers and request.headers['Origin'] in self.config['cors']:
                response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']

            return response

    def register_commands(self):
        """Register all application commands."""

        self.app.cli.add_command(update_timetable_command)
        self.app.cli.add_command(update_eclassroom_command)
        self.app.cli.add_command(create_database_command)
        self.app.cli.add_command(cleanup_database_command)

    def register_routes(self):
        """Register all application routes."""

        @self.app.route('/list/classes')
        def _list_classes():
            return jsonify([model.name for model in self.session.query(Class).order_by(Class.name)])

        @self.app.route('/list/teachers')
        def _list_teachers():
            return jsonify([model.name for model in self.session.query(Teacher).order_by(Teacher.name)])

        @self.app.route('/list/classrooms')
        def _list_classrooms():
            return jsonify([model.name for model in self.session.query(Classroom).order_by(Classroom.name)])

        @self.app.route('/timetable/classes/<classes>')
        def _get_timetable_for_classes(classes):
            classes = classes.split(',')
            return jsonify(list(Class.get_lessons(self.session, classes)))

        @self.app.route('/timetable/teachers/<teachers>')
        def _get_timetable_for_teachers(teachers):
            teachers = teachers.split(',')
            return jsonify(list(Teacher.get_lessons(self.session, teachers)))

        @self.app.route('/timetable/classrooms/<classrooms>')
        def _get_timetable_for_classrooms(classrooms):
            classrooms = classrooms.split(',')
            return jsonify(list(Classroom.get_lessons(self.session, classrooms)))

        @self.app.route('/timetable/classrooms/empty')
        def _get_timetable_for_empty_classrooms():
            return jsonify(list(Classroom.get_empty(self.session)))

        # TODO: Substitutions
        # TODO: Menus

        @self.app.route('/circulars')
        def _get_circulars():
            query = (self.session
                     .query(Document.date, Document.type, Document.url, Document.description)
                     .filter(Document.type.in_(('circular', 'other')))
                     .order_by(Document.date))

            return jsonify([{
                'date': model.date.strftime('%Y-%m-%d'),
                'type': model.type,
                'url': model.url,
                'description': model.description,

            } for model in query])


def create_app():
    """Application factory that accepts a configuration file from environment variable."""

    if 'GIMVICURNIK_CONFIG' in os.environ:
        configfile = os.environ.get('GIMVICURNIK_CONFIG')
    else:
        raise ConfigError('Missing config filename')

    gimvicurnik = GimVicUrnik(configfile)
    return gimvicurnik.app
