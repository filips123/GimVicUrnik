from .base import GimVicUrnikError

from .config import ConfigError, ConfigParseError, ConfigReadError, ConfigValidationError
from .eclassroom import (
    ClassroomApiError,
    ClassroomError,
    InvalidRecordError,
    InvalidTokenError,
    SubstitutionsFormatError,
    LunchScheduleFormatError,
    MenuFormatError,
)
from .timetable import TimetableApiError
