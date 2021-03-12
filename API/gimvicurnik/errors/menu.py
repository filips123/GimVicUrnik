from .base import GimVicUrnikError


class MenuError(GimVicUrnikError):
    pass


class MenuApiError(MenuError):
    pass


class MenuDateError(MenuError):
    pass


class MenuFormatError(MenuError):
    pass
