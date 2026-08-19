from __future__ import annotations

import enum
from collections.abc import Iterator
from datetime import date as date_, datetime, time as time_
from typing import Annotated, Any

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    SmallInteger,
    Text,
    UniqueConstraint,
    func,
    or_,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    aliased,
    mapped_column,
    relationship,
    scoped_session,
    sessionmaker,
)

# SQLAlchemy Session
SessionFactory = sessionmaker()
Session = scoped_session(SessionFactory)

# SQLALChemy Types
intpk = Annotated[int, mapped_column(primary_key=True)]
smallint = Annotated[int, mapped_column(SmallInteger())]
text = Annotated[str, mapped_column(Text())]
longtext = Annotated[str, mapped_column(Text(70000))]

# SQLAlchemy Relationships
class_fk = Annotated[int, mapped_column(ForeignKey("classes.id"))]
teacher_fk = Annotated[int, mapped_column(ForeignKey("teachers.id"))]
classroom_fk = Annotated[int, mapped_column(ForeignKey("classrooms.id"))]


@enum.unique
class DocumentType(enum.Enum):
    # Unparsable document types
    CIRCULAR = "circular"
    OTHER = "other"

    # Parsable document types
    TIMETABLE = "timetable"
    SUBSTITUTIONS = "substitutions"
    LUNCH_MENU = "lunch-menu"
    SNACK_MENU = "snack-menu"
    LUNCH_SCHEDULE = "lunch-schedule"

    @classmethod
    def names(cls, _obj: Any = None) -> list[str]:
        return [member.name for member in cls]

    @classmethod
    def values(cls, _obj: Any = None) -> list[str]:
        return [member.value for member in cls]

    @classmethod
    def column(cls) -> Enum:
        return Enum(cls, values_callable=cls.values)


class ValueEnum(enum.Enum):
    """Enum persisted using its stable string values."""

    @classmethod
    def values(cls, _obj: Any = None) -> list[str]:
        return [member.value for member in cls]

    @classmethod
    def column(cls) -> Enum:
        return Enum(cls, values_callable=cls.values)


@enum.unique
class SportType(ValueEnum):
    FOOTBALL = "football"
    VOLLEYBALL = "volleyball"
    BASKETBALL = "basketball"


@enum.unique
class SportsSeasonPhase(ValueEnum):
    SETUP = "setup"
    GROUP_STAGE = "group_stage"
    KNOCKOUT = "knockout"
    COMPLETED = "completed"


@enum.unique
class SportsMatchStage(ValueEnum):
    GROUP = "group"
    QUARTERFINAL = "quarterfinal"
    SEMIFINAL = "semifinal"
    THIRD_PLACE = "third_place"
    FINAL = "final"


@enum.unique
class SportsMatchStatus(ValueEnum):
    SCHEDULED = "scheduled"
    POSTPONED = "postponed"
    COMPLETED = "completed"
    FORFEITED = "forfeited"


@enum.unique
class SportsGroup(ValueEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[intpk]
    type: Mapped[DocumentType] = mapped_column(DocumentType.column(), index=True)

    created: Mapped[datetime | None]
    modified: Mapped[datetime | None]
    effective: Mapped[date_ | None]

    url: Mapped[text]
    title: Mapped[text | None]
    hash: Mapped[text | None]
    parsed: Mapped[bool | None]
    content: Mapped[longtext | None]


class Entity:
    __tablename__: str

    id: Mapped[intpk]
    name: Mapped[text] = mapped_column(unique=True, index=True)

    @classmethod
    def get_lessons(
        cls,
        names: list[str] | None = None,
    ) -> Iterator[dict[str, Any]]:
        query = (
            Session.query(Lesson, Class.name, Teacher.name, Classroom.name)
            .join(Class, isouter=True)
            .join(Teacher, isouter=True)
            .join(Classroom, isouter=True)
            .order_by(Lesson.day, Lesson.time)
        )

        if names:
            query = query.filter(cls.name.in_(names))

        for model in query:
            yield {
                "day": model[0].day,
                "time": model[0].time,
                "subject": model[0].subject,
                "class": model[1],
                "teacher": model[2],
                "classroom": model[3],
            }

    @classmethod
    def get_substitutions(
        cls,
        dates: list[date_] | None = None,
        names: list[str] | None = None,
    ) -> Iterator[dict[str, Any]]:
        original_teacher = aliased(Teacher)
        teacher = aliased(Teacher)

        original_classroom = aliased(Classroom)
        classroom = aliased(Classroom)

        # fmt: off
        query = (
            Session.query(Substitution, Class.name, original_teacher.name, original_classroom.name, teacher.name, classroom.name)
            .join(Class, isouter=True)
            .join(original_teacher, Substitution.original_teacher_id == original_teacher.id, isouter=True)
            .join(original_classroom, Substitution.original_classroom_id == original_classroom.id, isouter=True)
            .join(teacher, Substitution.teacher_id == teacher.id, isouter=True)
            .join(classroom, Substitution.classroom_id == classroom.id, isouter=True)
            .order_by(Substitution.day, Substitution.time)
        )
        # fmt: on

        if dates:
            query = query.filter(Substitution.date.in_(dates))

        if names:
            if cls.__tablename__ == "classes":
                query = query.filter(Class.name.in_(names))
            elif cls.__tablename__ == "teachers":
                query = query.filter(or_(original_teacher.name.in_(names), teacher.name.in_(names)))
            elif cls.__tablename__ == "classrooms":
                query = query.filter(or_(original_classroom.name.in_(names), classroom.name.in_(names)))

        for model in query:
            yield {
                "date": model[0].date.isoformat(),
                "day": model[0].day,
                "time": model[0].time,
                "subject": model[0].subject,
                "notes": model[0].notes,
                "class": model[1],
                "original-teacher": model[2],
                "original-classroom": model[3],
                "teacher": model[4],
                "classroom": model[5],
            }


class Class(Entity, Base):
    __tablename__ = "classes"


class Teacher(Entity, Base):
    __tablename__ = "teachers"


class Classroom(Entity, Base):
    __tablename__ = "classrooms"

    @classmethod
    def get_empty(cls) -> Iterator[dict[str, Any]]:
        days = (1, 5)
        times = Session.query(func.min(Lesson.time), func.max(Lesson.time))[0]

        if times[0] is None or times[1] is None:
            yield from ()
            return

        classrooms = Session.query(Classroom.name).order_by(Classroom.name).distinct().all()
        occupied = set(Session.query(Lesson.day, Lesson.time, Classroom.name).join(Classroom).distinct())

        for day in range(days[0], days[1] + 1):
            for time in range(times[0], times[1] + 1):
                for (classroom,) in classrooms:
                    if (day, time, classroom) not in occupied:
                        yield {
                            "day": day,
                            "time": time,
                            "subject": None,
                            "class": None,
                            "teacher": None,
                            "classroom": classroom,
                        }


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (Index("ix_lessons_day_time", "day", "time"),)

    id: Mapped[intpk]

    day: Mapped[smallint]
    time: Mapped[smallint]
    subject: Mapped[text | None]

    class_id: Mapped[class_fk | None] = mapped_column(index=True)
    class_: Mapped[Class | None] = relationship(backref="lessons")

    teacher_id: Mapped[teacher_fk | None] = mapped_column(index=True)
    teacher: Mapped[Teacher | None] = relationship(backref="lessons")

    classroom_id: Mapped[classroom_fk | None] = mapped_column(index=True)
    classroom: Mapped[Classroom | None] = relationship(backref="lessons")


class Substitution(Base):
    __tablename__ = "substitutions"
    __table_args__ = (Index("ix_substitutions_day_time", "day", "time"),)

    id: Mapped[intpk]
    date: Mapped[date_] = mapped_column(index=True)

    day: Mapped[smallint]
    time: Mapped[smallint]
    subject: Mapped[text | None]
    notes: Mapped[text | None]

    original_teacher_id: Mapped[teacher_fk | None] = mapped_column(index=True)
    original_teacher: Mapped[Teacher | None] = relationship(foreign_keys=[original_teacher_id])

    original_classroom_id: Mapped[classroom_fk | None] = mapped_column(index=True)
    original_classroom: Mapped[Classroom | None] = relationship(foreign_keys=[original_classroom_id])

    class_id: Mapped[class_fk | None] = mapped_column(index=True)
    class_: Mapped[Class | None] = relationship(backref="substitutions", foreign_keys=[class_id])

    teacher_id: Mapped[teacher_fk | None] = mapped_column(index=True)
    teacher: Mapped[Teacher | None] = relationship(backref="substitutions", foreign_keys=[teacher_id])

    classroom_id: Mapped[classroom_fk | None] = mapped_column(index=True)
    classroom: Mapped[Classroom | None] = relationship(backref="substitutions", foreign_keys=[classroom_id])


class LunchSchedule(Base):
    __tablename__ = "lunch_schedule"
    __table_args__ = (Index("ix_lunch_schedule_date_time", "date", "time"),)

    id: Mapped[intpk]
    date: Mapped[date_] = mapped_column(index=True)
    time: Mapped[time_ | None]

    class_id: Mapped[class_fk | None] = mapped_column(index=True)
    class_: Mapped[Class | None] = relationship()

    location: Mapped[text | None]
    notes: Mapped[text | None]


class SnackMenu(Base):
    __tablename__ = "snack_menu"

    id: Mapped[intpk]
    date: Mapped[date_] = mapped_column(unique=True, index=True)

    normal: Mapped[text | None]
    poultry: Mapped[text | None]
    vegetarian: Mapped[text | None]
    fruitvegetable: Mapped[text | None]


class LunchMenu(Base):
    __tablename__ = "lunch_menu"

    id: Mapped[intpk]
    date: Mapped[date_] = mapped_column(unique=True, index=True)

    until: Mapped[time_ | None]

    normal: Mapped[text | None]
    vegetarian: Mapped[text | None]


class SportsSeason(Base):
    __tablename__ = "sports_seasons"
    __table_args__ = (UniqueConstraint("sport", "school_year", name="uq_sports_season"),)

    id: Mapped[intpk]
    sport: Mapped[SportType] = mapped_column(SportType.column(), index=True)
    school_year: Mapped[str] = mapped_column(String(7), index=True)
    phase: Mapped[SportsSeasonPhase] = mapped_column(
        SportsSeasonPhase.column(), default=SportsSeasonPhase.SETUP
    )
    revision: Mapped[int] = mapped_column(Integer(), default=1)
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class SportsRule(Base):
    __tablename__ = "sports_rules"
    __table_args__ = (UniqueConstraint("season_id", "position", name="uq_sports_rule_position"),)

    id: Mapped[intpk]
    season_id: Mapped[int] = mapped_column(ForeignKey("sports_seasons.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(SmallInteger())
    text: Mapped[str] = mapped_column(Text())
    url: Mapped[str | None] = mapped_column(Text())

    season: Mapped[SportsSeason] = relationship(backref="rules")


class SportsParticipant(Base):
    __tablename__ = "sports_participants"
    __table_args__ = (UniqueConstraint("season_id", "class_code", name="uq_sports_participant"),)

    id: Mapped[intpk]
    season_id: Mapped[int] = mapped_column(ForeignKey("sports_seasons.id", ondelete="CASCADE"), index=True)
    class_code: Mapped[str] = mapped_column(String(2))
    group: Mapped[SportsGroup] = mapped_column(SportsGroup.column(), index=True)
    qualified_rank: Mapped[int | None] = mapped_column(SmallInteger())

    season: Mapped[SportsSeason] = relationship(backref="participants")


class SportsMatch(Base):
    __tablename__ = "sports_matches"
    __table_args__ = (
        Index("ix_sports_matches_date_status", "date", "status"),
        UniqueConstraint("season_id", "bracket_slot", name="uq_sports_bracket_slot"),
    )

    id: Mapped[intpk]
    season_id: Mapped[int] = mapped_column(ForeignKey("sports_seasons.id", ondelete="CASCADE"), index=True)
    stage: Mapped[SportsMatchStage] = mapped_column(SportsMatchStage.column(), index=True)
    status: Mapped[SportsMatchStatus] = mapped_column(
        SportsMatchStatus.column(), default=SportsMatchStatus.SCHEDULED
    )
    group: Mapped[SportsGroup | None] = mapped_column(SportsGroup.column(), index=True)
    bracket_slot: Mapped[str | None] = mapped_column(String(8))
    date: Mapped[date_ | None] = mapped_column(index=True)
    start_time: Mapped[time_] = mapped_column(default=time_(10, 30))

    home_participant_id: Mapped[int | None] = mapped_column(
        ForeignKey("sports_participants.id", ondelete="RESTRICT"), index=True
    )
    away_participant_id: Mapped[int | None] = mapped_column(
        ForeignKey("sports_participants.id", ondelete="RESTRICT"), index=True
    )
    home_participant: Mapped[SportsParticipant | None] = relationship(foreign_keys=[home_participant_id])
    away_participant: Mapped[SportsParticipant | None] = relationship(foreign_keys=[away_participant_id])

    home_score: Mapped[int | None] = mapped_column(Integer())
    away_score: Mapped[int | None] = mapped_column(Integer())
    home_penalties: Mapped[int | None] = mapped_column(Integer())
    away_penalties: Mapped[int | None] = mapped_column(Integer())
    forfeit_winner_id: Mapped[int | None] = mapped_column(
        ForeignKey("sports_participants.id", ondelete="RESTRICT"), index=True
    )
    notes: Mapped[text | None]
    revision: Mapped[int] = mapped_column(Integer(), default=1)
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    season: Mapped[SportsSeason] = relationship(backref="matches")
    forfeit_winner: Mapped[SportsParticipant | None] = relationship(foreign_keys=[forfeit_winner_id])
    volleyball_sets: Mapped[list[VolleyballSetScore]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )


class VolleyballSetScore(Base):
    __tablename__ = "volleyball_set_scores"
    __table_args__ = (UniqueConstraint("match_id", "set_number", name="uq_volleyball_match_set"),)

    id: Mapped[intpk]
    match_id: Mapped[int] = mapped_column(ForeignKey("sports_matches.id", ondelete="CASCADE"), index=True)
    set_number: Mapped[int] = mapped_column(SmallInteger())
    home_score: Mapped[int] = mapped_column(Integer())
    away_score: Mapped[int] = mapped_column(Integer())

    match: Mapped[SportsMatch] = relationship(back_populates="volleyball_sets")


class QualificationDecision(Base):
    __tablename__ = "sports_qualification_decisions"
    __table_args__ = (UniqueConstraint("season_id", "group", name="uq_sports_qualification_group"),)

    id: Mapped[intpk]
    season_id: Mapped[int] = mapped_column(ForeignKey("sports_seasons.id", ondelete="CASCADE"), index=True)
    group: Mapped[SportsGroup] = mapped_column(SportsGroup.column())
    ordered_classes_json: Mapped[text]
    reason: Mapped[text]

    season: Mapped[SportsSeason] = relationship(backref="qualification_decisions")


class SportsAuditEntry(Base):
    __tablename__ = "sports_audit_entries"

    id: Mapped[intpk]
    sport: Mapped[SportType] = mapped_column(SportType.column(), index=True)
    school_year: Mapped[str] = mapped_column(String(7), index=True)
    action: Mapped[str] = mapped_column(String(80))
    record_type: Mapped[str] = mapped_column(String(80))
    record_id: Mapped[int | None] = mapped_column(Integer())
    before_json: Mapped[longtext | None]
    after_json: Mapped[longtext | None]
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
