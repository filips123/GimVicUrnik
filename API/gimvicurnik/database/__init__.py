from sqlalchemy import func, Column, Index, ForeignKey, Integer, Date, Text, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
Session = sessionmaker()


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)

    date = Column(Date)
    type = Column(Text)
    url = Column(Text)
    hash = Column(Text, nullable=True)
    description = Column(Text, nullable=True)


class Entity:
    id = Column(Integer, primary_key=True)
    name = Column(Text)

    @classmethod
    def get_lessons(cls, session, names):
        query = (session
                 .query(Lesson, Class.name, Teacher.name, Classroom.name)
                 .filter(cls.name.in_(names))
                 .join(Class)
                 .join(Teacher)
                 .join(Classroom)
                 .order_by(Lesson.day, Lesson.time))

        for model in query:
            yield {
                'day': model[0].day,
                'time': model[0].time,
                'subject': model[0].subject,
                'class': model[1],
                'teacher': model[2],
                'classroom': model[3],
            }


class Class(Entity, Base):
    __tablename__ = 'classes'


class Teacher(Entity, Base):
    __tablename__ = 'teachers'


class Classroom(Entity, Base):
    __tablename__ = 'classrooms'

    @classmethod
    def get_empty(cls, session):
        days = (1, 5)
        times = session.query(func.min(Lesson.time), func.max(Lesson.time))[0]

        classrooms = list(session.query(Classroom).order_by(Classroom.name))
        lessons = list(session.query(Lesson).join(Classroom))

        for day in range(days[0], days[1]+1):
            for time in range(times[0], times[1]+1):
                for classroom in classrooms:
                    is_classroom_empty = True

                    for lesson in lessons:
                        if lesson.day == day and lesson.time == time and lesson.classroom == classroom:
                            is_classroom_empty = False
                            break

                    if is_classroom_empty:
                        yield {
                            'day': day,
                            'time': time,
                            'subject': None,
                            'class': None,
                            'teacher': None,
                            'classroom': classroom.name,
                        }


class Lesson(Base):
    __tablename__ = 'lessons'
    __table_args__ = (Index('ix_lessons_day_time', 'day', 'time'), )

    id = Column(Integer, primary_key=True)

    day = Column(SmallInteger)
    time = Column(SmallInteger)
    subject = Column(Text, nullable=True)

    class_id = Column(Integer, ForeignKey('classes.id'), index=True)
    class_ = relationship('Class', backref='lessons')

    teacher_id = Column(Integer, ForeignKey('teachers.id'), index=True)
    teacher = relationship('Teacher', backref='lessons')

    classroom_id = Column(Integer, ForeignKey('classrooms.id'), index=True)
    classroom = relationship('Classroom', backref='lessons')


class Substitution(Base):
    __tablename__ = 'substitutions'
    __table_args__ = (Index('ix_substitutions_day_time', 'day', 'time'), )

    id = Column(Integer, primary_key=True)
    date = Column(Date)

    day = Column(SmallInteger)
    time = Column(SmallInteger)
    subject = Column(Text, nullable=True)

    original_teacher_id = Column(Integer, ForeignKey('teachers.id'))
    original_teacher = relationship('Teacher', foreign_keys=[original_teacher_id])

    class_id = Column(Integer, ForeignKey('classes.id'), index=True)
    class_ = relationship('Class', backref='substitutions', foreign_keys=[class_id])

    teacher_id = Column(Integer, ForeignKey('teachers.id'), index=True)
    teacher = relationship('Teacher', backref='substitutions', foreign_keys=[teacher_id])

    classroom_id = Column(Integer, ForeignKey('classrooms.id'), index=True)
    classroom = relationship('Classroom', backref='substitutions', foreign_keys=[classroom_id])
