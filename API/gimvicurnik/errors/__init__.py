from .base import GimVicUrnikError
from .circulars import CircularsApiError, InvalidIdentifierError, OrphanedAttachmentError
from .config import ConfigError, ConfigParseError, ConfigReadError, ConfigValidationError
from .eclassroom import (
    ClassroomApiError,
    ClassroomError,
    InvalidRecordError,
    InvalidTokenError,
    LunchScheduleFormatError,
    SubstitutionsFormatError,
)
from .menu import MenuApiError, MenuDateError, MenuFormatError
from .solsis import SolsisApiError
from .timetable import TimetableApiError
