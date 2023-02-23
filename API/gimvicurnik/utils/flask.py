from __future__ import annotations

import typing
from datetime import datetime

from werkzeug.routing import BaseConverter
from werkzeug.routing.converters import ValidationError

if typing.TYPE_CHECKING:
    from datetime import date
    from typing import Any


class DateConverter(BaseConverter):
    """Extract a ISO8601 date from the path and validate it."""

    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value: str) -> date:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as error:
            raise ValidationError() from error

    def to_url(self, value: date) -> str:
        return value.strftime("%Y-%m-%d")


class ListConverter(BaseConverter):
    """Extract a comma-separated list from the path."""

    def to_python(self, value: str) -> list[str]:
        return value.split(",")

    def to_url(self, value: list[Any]) -> str:
        return ",".join(str(x) for x in value)
