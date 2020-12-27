import datetime
import hashlib
import logging
import os
import re
import tempfile

import requests
from pdf2docx import extract_tables

from ..database import Document, Class, Teacher, Classroom, Substitution, LunchSchedule
from ..errors import InvalidTokenError, InvalidRecordError, ClassroomApiError
from ..utils.database import get_or_create
from ..utils.sentry import with_span


class EClassroomUpdater:
    def __init__(self, config, session):
        self.url = config['url']
        self.token = config['token']
        self.course = config['course']
        self.restricted = config['restricted']
        self.session = session
        self.logger = logging.getLogger(__name__)

    def update(self):
        for name, url, date in self._get_documents():
            if 'www.dropbox.com' in url:
                self._store_substitutions(name, url.replace('dl=0', 'dl=1'))
            elif 'delitevKosila' in url:
                self._store_lunch_schedule(name, url)
            elif 'okroznica' in url:
                self._store_generic(name, url, date, 'circular')
            else:
                self._store_generic(name, url, date, 'other')

    def _get_documents(self):
        params = {
            'moodlewsrestformat': 'json',
        }
        data = {
            'courseid': self.course,
            'wstoken': self.token,
            'wsfunction': 'core_course_get_contents',
        }

        try:
            response = requests.post(self.url, params=params, data=data)
            objects = response.json()

            response.raise_for_status()
        except (IOError, ValueError) as error:
            raise ClassroomApiError('Error while accessing e-classroom API') from error

        # Handle API errors
        if 'errorcode' in objects:
            if objects['errorcode'] == 'invalidtoken':
                raise InvalidTokenError(objects['message'])
            elif objects['errorcode'] == 'invalidrecord':
                raise InvalidRecordError(objects['message'])
            else:
                raise ClassroomApiError(objects['message'])

        # Yield every document name, URL and date
        for object in objects:
            for module in object['modules']:
                if 'contents' not in module:
                    continue

                yield (
                    module['name'],
                    self._tokenize_url(module['contents'][0]['fileurl']),
                    datetime.datetime.fromtimestamp(module['contents'][0]['timecreated']).date(),
                )

    def _tokenize_url(self, url):
        # Add token to all restricted URLs
        if any(map(url.__contains__, self.restricted)):
            request = requests.PreparedRequest()
            request.prepare_url(url, {'token': self.token})
            return request.url

    @with_span(op='document', pass_span=True)
    def _store_generic(self, name, url, date, urltype, span):
        # Add or skip new generic document
        model, created = get_or_create(
            session=self.session,
            model=Document,
            date=date,
            type=urltype,
            url=url,
            description=name
        )

        span.description = model.url
        span.set_tag('document.url', model.url)
        span.set_tag('document.type', model.type)
        span.set_tag('document.date', model.date)
        span.set_tag('document.action', 'created' if created else 'skipped')

        if created:
            self.logger.info('Created a new %s document', urltype)
        else:
            self.logger.info('Skipped because the %s document is already stored', urltype)
        self.logger.debug('URL: %s', model.url)
        self.logger.debug('Type: %s', model.type)
        self.logger.debug('Created: %s', model.date)

    @with_span(op='document', pass_span=True)
    def _store_substitutions(self, name, url, span):
        response = requests.get(url)

        content = response.content
        hash = str(hashlib.sha256(content).hexdigest())

        span.description = url
        span.set_tag('document.url', url)
        span.set_tag('document.type', 'substitutions')

        # Skip unchanged substitutions documents
        document = self.session.query(Document).filter(Document.type == 'substitutions', Document.url == url).first()
        if hash == getattr(document, 'hash', False):
            self.logger.info('Skipped because the substitutions document for %s is unchanged', document.date)
            self.logger.debug('URL: %s', document.url)
            self.logger.debug('Date: %s', document.date)
            self.logger.debug('Hash: %s', document.hash)

            span.set_tag('document.date', document.date)
            span.set_tag('document.hash', document.hash)
            span.set_tag('document.action', 'skipped')

            return

        date = datetime.datetime.strptime(re.search(r'_obvestila_(.+).pdf', url, re.IGNORECASE).group(1), '%d._%m._%Y').date()
        day = date.isoweekday()

        filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex() + '.pdf')

        file = open(filename, mode='w+b')
        file.write(content)
        file.close()

        # Extract all tables from PDF file
        tables = with_span(op='extract')(extract_tables)(filename)
        os.remove(filename)

        header_substitutions = ['ODSOTNI UČITELJ/ICA', 'URA', 'RAZRED', 'UČILNICA', 'NADOMEŠČA', 'PREDMET', 'OPOMBA']
        header_lesson_change = ['RAZRED', 'URA', 'UČITELJ/ICA', 'PREDMETA', 'UČILNICA', 'OPOMBA']
        header_classroom_change = ['RAZRED', 'URA', 'UČITELJ/ICA', 'PREDMET', 'IZ UČILNICE', 'V UČILNICO', 'OPOMBA']
        header_more_teachers = ['URA', 'UČITELJ', 'RAZRED', 'UČILNICA', 'OPOMBA']
        header_reservations = ['URA', 'UČILNICA', 'REZERVIRAL/A', 'OPOMBA']

        substitutions = []

        parser_type = None
        last_original_teacher = None

        # Parse tables into substitutions
        for table in tables:
            for row in table:
                row = [column.replace('\n', ' ').strip() if column else None for column in row]

                # Get parser type
                if row == header_substitutions:
                    parser_type = 'substitutions'
                    continue
                elif row == header_lesson_change:
                    parser_type = 'lesson-change'
                    continue
                elif row == header_classroom_change:
                    parser_type = 'classroom-change'
                    continue
                elif row == header_more_teachers:
                    parser_type = 'more-teachers'
                    continue
                elif row == header_reservations:
                    parser_type = 'reservations'
                    continue

                # Parse substitutions
                if parser_type == 'substitutions':
                    time = row[1][:-1]
                    subject = row[5] if row[5] != '/' else None

                    # Get original teacher
                    # Special cases: Replace ć with č, multiple Krapež teachers
                    original_teacher = row[0].split()[0].replace('ć', 'č') if row[0] else last_original_teacher
                    if original_teacher == 'Krapež':
                        if 'Alenka' in row[0]:
                            original_teacher = 'KrapežA'
                        elif 'Marjetka' in row[0]:
                            original_teacher = 'KrapežM'
                    last_original_teacher = original_teacher

                    original_classroom = row[3]

                    # Handle multiple classes
                    classes = row[2].replace('. ', '').split(' - ')
                    classes = classes[:-1] if len(classes) > 1 else classes

                    # Get new teacher
                    # Special cases: Replace ć with č, multiple Krapež teachers
                    teacher = row[4].split()[0].replace('ć', 'č')
                    if teacher == 'Krapež':
                        if 'Alenka' in row[4]:
                            teacher = 'KrapežA'
                        elif 'Marjetka' in row[4]:
                            teacher = 'KrapežM'
                    classroom = original_classroom

                    for class_ in classes:
                        substitutions.append({
                            'date': date,
                            'day': day,
                            'time': time,
                            'subject': subject,
                            'original_teacher_id': get_or_create(self.session, model=Teacher, name=original_teacher)[0].id,
                            'original_classroom_id': get_or_create(self.session, model=Classroom, name=original_classroom)[0].id if original_classroom else None,
                            'class_id': get_or_create(self.session, model=Class, name=class_)[0].id,
                            'teacher_id': get_or_create(self.session, model=Teacher, name=teacher)[0].id if teacher != '/' else None,
                            'classroom_id': get_or_create(self.session, model=Classroom, name=classroom)[0].id if classroom else None,
                        })

                elif parser_type == 'lesson-change':
                    time = row[1][:-1]
                    subject = row[3].split(' → ')[1]

                    # Get original teacher
                    # Special cases: Replace ć with č, multiple Krapež teachers
                    original_teacher = row[2].split(' → ')[0].split()[0].replace('ć', 'č')
                    if original_teacher == 'Krapež':
                        if 'Alenka' in row[2].split(' → ')[0]:
                            original_teacher = 'KrapežA'
                        elif 'Marjetka' in row[2].split(' → ')[0]:
                            original_teacher = 'KrapežM'

                    original_classroom = row[4]

                    # Handle multiple classes
                    classes = row[0].replace('. ', '').split(' - ')
                    classes = classes[:-1] if len(classes) > 1 else classes

                    # Get new teacher
                    # Special cases: Replace ć with č, multiple Krapež teachers
                    teacher = row[2].split(' → ')[1].split()[0].replace('ć', 'č')
                    if teacher == 'Krapež':
                        if 'Alenka' in row[2].split(' → ')[1]:
                            teacher = 'KrapežA'
                        elif 'Marjetka' in row[2].split(' → ')[1]:
                            teacher = 'KrapežM'
                    classroom = original_classroom

                    for class_ in classes:
                        substitutions.append({
                            'date': date,
                            'day': day,
                            'time': time,
                            'subject': subject,
                            'original_teacher_id': get_or_create(self.session, model=Teacher, name=original_teacher)[0].id,
                            'original_classroom_id': get_or_create(self.session, model=Classroom, name=original_classroom)[0].id,
                            'class_id': get_or_create(self.session, model=Class, name=class_)[0].id,
                            'teacher_id': get_or_create(self.session, model=Teacher, name=teacher)[0].id,
                            'classroom_id': get_or_create(self.session, model=Classroom, name=classroom)[0].id,
                        })

                elif parser_type == 'classroom-change':
                    time = row[1][:-1]
                    subject = row[3]

                    # Get teacher
                    # Special cases: Replace ć with č, multiple Krapež teachers
                    original_teacher = row[2].split()[0].replace('ć', 'č')
                    if original_teacher == 'Krapež':
                        if 'Alenka' in row[2]:
                            original_teacher = 'KrapežA'
                        elif 'Marjetka' in row[2]:
                            original_teacher = 'KrapežM'

                    original_classrooms = row[4].split(', ')

                    # Handle multiple classes
                    classes = row[0].replace('. ', '').split(' - ')
                    classes = classes[:-1] if len(classes) > 1 else classes

                    teacher = original_teacher
                    classroom = row[5]

                    for class_ in classes:
                        for original_classroom in original_classrooms:
                            substitutions.append({
                                'date': date,
                                'day': day,
                                'time': time,
                                'subject': subject,
                                'original_teacher_id': get_or_create(self.session, model=Teacher, name=original_teacher)[0].id,
                                'original_classroom_id': get_or_create(self.session, model=Classroom, name=original_classroom)[0].id,
                                'class_id': get_or_create(self.session, model=Class, name=class_)[0].id,
                                'teacher_id': get_or_create(self.session, model=Teacher, name=teacher)[0].id,
                                'classroom_id': get_or_create(self.session, model=Classroom, name=classroom)[0].id,
                            })

        # Store substitutions in database
        for substitution in substitutions:
            model = (self.session
                     .query(Substitution)
                     .filter(
                        Substitution.date == substitution['date'],
                        Substitution.time == substitution['time'],
                        Substitution.original_teacher_id == substitution['original_teacher_id'],
                        Substitution.class_id == substitution['class_id'])
                     .first())

            # Update or create a substitution
            if not model:
                model = Substitution()

            for key in substitution:
                setattr(model, key, substitution[key])

            self.session.add(model)

        # Update or create a document
        if not document:
            document = Document()
            created = True
        else:
            created = False

        document.date = date
        document.type = 'substitutions'
        document.url = url
        document.description = name
        document.hash = hash

        self.session.add(document)

        span.set_tag('document.date', document.date)
        span.set_tag('document.hash', document.hash)
        span.set_tag('document.action', 'created' if created else 'updated')

        if created:
            self.logger.info('Created a new substitutions document for %s', document.date)
        else:
            self.logger.info('Updated the substitutions document for %s', document.date)

    @with_span(op='document', pass_span=True)
    def _store_lunch_schedule(self, name, url, span):
        response = requests.get(url)

        content = response.content
        hash = str(hashlib.sha256(content).hexdigest())

        span.description = url
        span.set_tag('document.url', url)
        span.set_tag('document.type', 'lunch-schedule')

        # Skip unchanged lunch schedule document documents
        document = self.session.query(Document).filter(Document.type == 'lunch-schedule', Document.url == url).first()
        if hash == getattr(document, 'hash', False):
            self.logger.info('Skipped because the lunch schedule document for %s is unchanged', document.date)
            self.logger.debug('URL: %s', document.url)
            self.logger.debug('Date: %s', document.date)
            self.logger.debug('Hash: %s', document.hash)

            span.set_tag('document.date', document.date)
            span.set_tag('document.hash', document.hash)
            span.set_tag('document.action', 'skipped')

            return

        date = datetime.datetime.strptime(re.search(r'Razpored delitve kosila, (.+)', name, re.IGNORECASE).group(1), '%d. %m. %Y').date()

        filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex() + '.pdf')

        file = open(filename, mode='w+b')
        file.write(content)
        file.close()

        # Extract all tables from PDF file
        tables = with_span(op='extract')(extract_tables)(filename)
        os.remove(filename)

        schedule = []

        last_hour = None
        last_notes = None

        for table in tables:
            # Skip instructions
            if 'Dijaki prihajate v jedilnico' in table[0][0]:
                continue

            for row in table:
                # Skip header
                if row[0] and 'ura' in row[0]:
                    continue

                time = datetime.datetime.strptime(row[0].strip(), '%H:%M').time() if row[0] else last_hour
                last_hour = time

                notes = row[1] if row[1] else last_notes
                last_notes = notes.strip()

                class_ = row[2].strip()
                location = row[4].strip()

                schedule.append({
                    'class_id': get_or_create(self.session, model=Class, name=class_)[0].id,
                    'date': date,
                    'time': time,
                    'location': location,
                    'notes': notes,
                })

        # Store schedule in database
        self.session.query(LunchSchedule).filter(LunchSchedule.date == date).delete()
        self.session.bulk_insert_mappings(LunchSchedule, schedule)

        # Update or create a document
        if not document:
            document = Document()
            created = True
        else:
            created = False

        document.date = date
        document.type = 'lunch-schedule'
        document.url = url
        document.description = name
        document.hash = hash

        self.session.add(document)

        span.set_tag('document.date', document.date)
        span.set_tag('document.hash', document.hash)
        span.set_tag('document.action', 'created' if created else 'updated')

        if created:
            self.logger.info('Created a new lunch schedule document for %s', document.date)
        else:
            self.logger.info('Updated the lunch schedule document for %s', document.date)
