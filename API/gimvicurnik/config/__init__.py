from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

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
class ConfigSources:
    timetable: ConfigSourcesTimetable
    eclassroom: ConfigSourcesEClassroom


# --------- URLS CONFIG ---------


@define(kw_only=True)
class ConfigURLs:
    website: str
    api: str


# -------- SENTRY CONFIG ---------


@define(kw_only=True)
class ConfigSentryTracesSampleRate:
    commands: float | int | bool = field(default=1.0, converter=_identity_convertor)
    requests: float | int | bool = field(default=1.0, converter=_identity_convertor)
    other: float | int | bool = field(default=1.0, converter=_identity_convertor)


@define(kw_only=True)
class ConfigSentryProfilerSampleRate:
    commands: float | int | bool = field(default=False, converter=_identity_convertor)
    requests: float | int | bool = field(default=False, converter=_identity_convertor)
    other: float | int | bool = field(default=False, converter=_identity_convertor)


@define(kw_only=True)
class ConfigSentry:
    dsn: str
    enabled: bool = True
    collectIPs: bool = False
    releasePrefix: str = ""
    releaseSuffix: str = ""
    maxBreadcrumbs: int = 100
    tracesSampleRate: ConfigSentryTracesSampleRate = Factory(ConfigSentryTracesSampleRate)
    profilerSampleRate: ConfigSentryProfilerSampleRate = Factory(ConfigSentryProfilerSampleRate)


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
    cors: list[str] = Factory(list)
    sentry: ConfigSentry | None = None
    logging: dict | str | None = field(default=None, converter=_identity_convertor)
    lessonTimes: list[ConfigLessonTime]
