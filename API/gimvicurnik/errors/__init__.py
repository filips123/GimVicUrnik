from .base import GimVicUrnikError

from .config import ConfigError, ConfigParseError, ConfigReadError, ConfigValidationError
from .eclassroom import (
    ClassroomApiError,
    ClassroomError,
    InvalidRecordError,
    InvalidTokenError,
    SubstitutionsFormatError,
    LunchScheduleFormatError,
)
from .menu import MenuApiError, MenuDateError, MenuFormatError
from .timetable import TimetableApiError
