from __future__ import annotations

import enum
import typing

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
    Time,
    func,
    or_,
)
from sqlalchemy.orm import aliased, declarative_base, relationship, scoped_session, sessionmaker

if typing.TYPE_CHECKING:
    import datetime
    from typing import Any, Dict, Iterator, List, Optional

Base = declarative_base()

SessionFactory = sessionmaker()
Session = scoped_session(SessionFactory)


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
    def names(cls, _obj: Any = None) -> List[str]:
        return [member.name for member in cls]

    @classmethod
    def values(cls, _obj: Any = None) -> List[str]:
        return [member.value for member in cls]


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    type = Column(Enum(DocumentType, values_callable=DocumentType.values), index=True)

    created = Column(DateTime, nullable=True)
    modified = Column(DateTime, nullable=True)
    effective = Column(Date, nullable=True)

    url = Column(Text)
    title = Column(Text, nullable=True)
    hash = Column(Text, nullable=True)
    parsed = Column(Boolean, nullable=True)
    content = Column(Text, nullable=True)


class Entity:
    __tablename__: str

    id = Column(Integer, primary_key=True)
    name = Column(Text)

    @classmethod
    def get_lessons(
        cls,
        names: Optional[List[str]] = None,
    ) -> Iterator[Dict[str, Any]]:
        query = (
            Session.query(Lesson, Class.name, Teacher.name, Classroom.name)
            .join(Class)
            .join(Teacher)
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
        date: Optional[datetime.date] = None,
        names: Optional[List[str]] = None,
    ) -> Iterator[Dict[str, Any]]:
        original_teacher = aliased(Teacher)
        teacher = aliased(Teacher)

        original_classroom = aliased(Classroom)
        classroom = aliased(Classroom)

        # fmt: off
        query = (
            Session.query(Substitution, Class.name, original_teacher.name, original_classroom.name, teacher.name, classroom.name)
            .join(Class)
            .join(original_teacher, Substitution.original_teacher_id == original_teacher.id, isouter=True)
            .join(original_classroom, Substitution.original_classroom_id == original_classroom.id, isouter=True)
            .join(teacher, Substitution.teacher_id == teacher.id, isouter=True)
            .join(classroom, Substitution.classroom_id == classroom.id, isouter=True)
            .order_by(Substitution.day, Substitution.time)
        )
        # fmt: on

        if date:
            query = query.filter(Substitution.date == date)

        if names:
            if cls.__tablename__ == "classes":
                query = query.filter(Class.name.in_(names))
            elif cls.__tablename__ == "teachers":
                query = query.filter(or_(original_teacher.name.in_(names), teacher.name.in_(names)))
            elif cls.__tablename__ == "classrooms":
                query = query.filter(or_(original_classroom.name.in_(names), classroom.name.in_(names)))

        for model in query:
            yield {
                "date": model[0].date.strftime("%Y-%m-%d"),
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
    def get_empty(cls) -> Iterator[Dict[str, Any]]:
        days = (1, 5)
        times = Session.query(func.min(Lesson.time), func.max(Lesson.time))[0]

        if times[0] is None or times[1] is None:
            return []

        classrooms = list(Session.query(Classroom).order_by(Classroom.name))
        lessons = list(Session.query(Lesson).join(Classroom))

        for day in range(days[0], days[1] + 1):
            for time in range(times[0], times[1] + 1):
                for classroom in classrooms:
                    is_classroom_empty = True

                    for lesson in lessons:
                        if lesson.day == day and lesson.time == time and lesson.classroom == classroom:
                            is_classroom_empty = False
                            break

                    if is_classroom_empty:
                        yield {
                            "day": day,
                            "time": time,
                            "subject": None,
                            "class": None,
                            "teacher": None,
                            "classroom": classroom.name,
                        }


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (Index("ix_lessons_day_time", "day", "time"),)

    id = Column(Integer, primary_key=True)

    day = Column(SmallInteger)
    time = Column(SmallInteger)
    subject = Column(Text, nullable=True)

    class_id = Column(Integer, ForeignKey("classes.id"), index=True)
    class_: Class = relationship("Class", backref="lessons")

    teacher_id = Column(Integer, ForeignKey("teachers.id"), index=True)
    teacher: Teacher = relationship("Teacher", backref="lessons")

    classroom_id = Column(Integer, ForeignKey("classrooms.id"), index=True)
    classroom: Classroom = relationship("Classroom", backref="lessons")


class Substitution(Base):
    __tablename__ = "substitutions"
    __table_args__ = (Index("ix_substitutions_day_time", "day", "time"),)

    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True)

    day = Column(SmallInteger)
    time = Column(SmallInteger)
    subject = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    original_teacher_id = Column(Integer, ForeignKey("teachers.id"))
    original_teacher: Teacher = relationship("Teacher", foreign_keys=[original_teacher_id])

    original_classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    original_classroom: Classroom = relationship("Classroom", foreign_keys=[original_classroom_id])

    class_id = Column(Integer, ForeignKey("classes.id"), index=True)
    class_: Class = relationship("Class", backref="substitutions", foreign_keys=[class_id])

    teacher_id = Column(Integer, ForeignKey("teachers.id"), index=True)
    teacher: Teacher = relationship("Teacher", backref="substitutions", foreign_keys=[teacher_id])

    classroom_id = Column(Integer, ForeignKey("classrooms.id"), index=True)
    classroom: Classroom = relationship("Classroom", backref="substitutions", foreign_keys=[classroom_id])


class LunchSchedule(Base):
    __tablename__ = "lunch_schedule"
    __table_args__ = (Index("ix_lunch_schedule_date_time", "date", "time"),)

    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True)
    time = Column(Time)

    class_id = Column(Integer, ForeignKey("classes.id"), index=True)
    class_: Class = relationship("Class")

    location = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)


class SnackMenu(Base):
    __tablename__ = "snack_menu"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, index=True)

    normal = Column(Text, nullable=True)
    poultry = Column(Text, nullable=True)
    vegetarian = Column(Text, nullable=True)
    fruitvegetable = Column(Text, nullable=True)


class LunchMenu(Base):
    __tablename__ = "lunch_menu"

    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, index=True)

    normal = Column(Text, nullable=True)
    vegetarian = Column(Text, nullable=True)
