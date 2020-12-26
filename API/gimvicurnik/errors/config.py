from schema import SchemaError
from yaml import YAMLError

from .base import GimVicUrnikError


class ConfigError(GimVicUrnikError):
    pass


class ConfigReadError(ConfigError, OSError):
    pass


class ConfigParseError(ConfigError, YAMLError):
    pass


class ConfigValidationError(ConfigError, SchemaError):
    pass
