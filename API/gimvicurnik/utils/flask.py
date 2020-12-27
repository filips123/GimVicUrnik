from datetime import datetime
from werkzeug.routing import BaseConverter, ValidationError


class DateConverter(BaseConverter):
    """Extract a ISO8601 date from the path and validate it."""

    regex = r'\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError()

    def to_url(self, value):
        return value.strftime('%Y-%m-%d')


class ListConverter(BaseConverter):
    """Extract a comma-separated list from the path."""

    def to_python(self, value):
        return value.split(',')

    def to_url(self, value):
        return ','.join(str(x) for x in value)
