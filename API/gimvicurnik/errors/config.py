from .base import GimVicUrnikError


class ConfigError(GimVicUrnikError):
    pass


class ConfigReadError(ConfigError):
    pass


class ConfigParseError(ConfigError):
    pass


class ConfigValidationError(ConfigError):
    pass
