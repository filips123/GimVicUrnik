from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, List, Optional, Union

from attrs import Factory, define, field


# =========== CUSTOM CONVERTORS ============


def _timedelta_convertor(value: str) -> timedelta:
    parsed = datetime.strptime(value, "%H%M")
    return timedelta(hours=parsed.hour, minutes=parsed.minute)


def _identity_convertor(value: Any) -> Any:
    return value


# =========== CONFIG DEFINITIONS ===========


# -------- SOURCES CONFIG --------


@define(kw_only=True)
class ConfigSourcesTimetable:
    url: str


@define(kw_only=True)
class ConfigSourcesEClassroom:
    token: str
    webserviceUrl: str
    pluginFileWebserviceUrl: str
    pluginFileNormalUrl: str
    course: int


@define(kw_only=True)
class ConfigSourcesMenu:
    url: str


@define(kw_only=True)
class ConfigSources:
    timetable: ConfigSourcesTimetable
    eclassroom: ConfigSourcesEClassroom
    menu: ConfigSourcesMenu


# --------- URLS CONFIG ---------


@define(kw_only=True)
class ConfigURLs:
    website: str
    api: str


# -------- SENTRY CONFIG ---------


@define(kw_only=True)
class ConfigSentrySampleRate:
    commands: Union[float, int, bool] = field(default=1.0, converter=_identity_convertor)
    requests: Union[float, int, bool] = field(default=0.5, converter=_identity_convertor)
    other: Union[float, int, bool] = field(default=0.5, converter=_identity_convertor)


@define(kw_only=True)
class ConfigSentry:
    dsn: str
    enabled: bool = True
    collectIPs: bool = False
    releasePrefix: str = ""
    releaseSuffix: str = ""
    maxBreadcrumbs: int = 100
    sampleRate: ConfigSentrySampleRate = Factory(ConfigSentrySampleRate)


# ------ LESSON TIME CONFIG ------


@define(kw_only=True)
class ConfigLessonTime:
    name: str
    start: timedelta = field(converter=_timedelta_convertor)
    end: timedelta = field(converter=_timedelta_convertor)


# --------- MAIN CONFIG ----------


@define(kw_only=True)
class Config:
    sources: ConfigSources
    urls: ConfigURLs
    database: str
    cors: List[str] = Factory(list)
    sentry: Optional[ConfigSentry] = None
    logging: Optional[Union[dict, str]] = field(default=None, converter=_identity_convertor)
    lessonTimes: List[ConfigLessonTime]
