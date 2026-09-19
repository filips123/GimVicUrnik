from .base import GimVicUrnikError


class CircularsError(GimVicUrnikError):
    pass


class CircularsApiError(CircularsError):
    pass


class InvalidIdentifierError(CircularsError):
    pass


class OrphanedAttachmentError(CircularsError):
    pass
