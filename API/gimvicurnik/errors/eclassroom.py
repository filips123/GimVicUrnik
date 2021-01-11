from .base import GimVicUrnikError


class ClassroomApiError(GimVicUrnikError):
    pass


class InvalidTokenError(ClassroomApiError):
    pass


class InvalidRecordError(ClassroomApiError):
    pass
