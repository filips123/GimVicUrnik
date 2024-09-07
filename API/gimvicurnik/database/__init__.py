from __future__ import annotations

import enum
from collections.abc import Iterator
from datetime import date as date_, datetime, time as time_
from typing import Annotated, Any

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    SmallInteger,
    Text,
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
