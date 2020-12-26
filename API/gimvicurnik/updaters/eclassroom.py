import datetime
import hashlib
import logging
import re
from tempfile import TemporaryFile

import requests

from ..database import Document
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

        response = requests.post(self.url, params=params, data=data)
        objects = response.json()

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

        with TemporaryFile() as file:
            file.write(content)

            # TODO:
            #  Parse PDF file using pdf2docx
            #  Extract all substitutions and store them in database

        # Update or create a document
        if not document:
            document = Document()
            created = True
        else:
            created = False

        document.date = datetime.datetime.strptime(re.search(r'_obvestila_(.+).pdf', url, re.IGNORECASE).group(1), '%d._%m._%Y').date()
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
        # TODO: Store and parse lunch schedule
        pass
