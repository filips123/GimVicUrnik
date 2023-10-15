from .base import GimVicUrnikError


class ClassroomError(GimVicUrnikError):
    pass


class ClassroomApiError(ClassroomError):
    pass


class InvalidTokenError(ClassroomApiError):
    pass


class InvalidRecordError(ClassroomApiError):
    pass


class SubstitutionsFormatError(ClassroomError):
    pass


class LunchScheduleFormatError(ClassroomError):
    pass


class MenuFormatError(ClassroomError):
    pass
