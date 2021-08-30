import datetime
import random
from random import choice, randint

from ..database import Class, Classroom, Substitution, Teacher


class SubstitutionsGenerator:
    def __init__(self, session, number):
        self.session = session
        self.number = int(number)

    def generate(self):
        substitutions = []

        # Parse tables into substitutions
        for _ in range(self.number):
            date = datetime.datetime.now() + datetime.timedelta(days=randint(0, 14))
            day = date.isoweekday()

            substitutions.append(
                {
                    "date": date,
                    "day": day,
                    "time": randint(0, 8),
                    "subject": choice(["MAT", "SLO", "ANG", "NEM", "KEM", "FIZ"]),
                    "original_teacher_id": self.session.query(Teacher)[
                        random.randrange(0, self.session.query(Teacher).count())
                    ].id,
                    "original_classroom_id": self.session.query(Classroom)[
                        random.randrange(0, self.session.query(Classroom).count())
                    ].id,
                    "class_id": self.session.query(Class)[random.randrange(0, self.session.query(Class).count())].id,
                    "teacher_id": self.session.query(Teacher)[random.randrange(0, self.session.query(Teacher).count())].id,
                    "classroom_id": self.session.query(Classroom)[random.randrange(0, self.session.query(Classroom).count())].id,
                }
            )

        # Store substitutions in database
        substitutions = [dict(element) for element in {tuple(substitution.items()) for substitution in substitutions}]
        self.session.bulk_insert_mappings(Substitution, substitutions)
