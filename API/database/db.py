from .base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


class db:
    def __init__(self, config):
        self.engine = create_engine(config["engine"])
        self.base = Base
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = scoped_session(Session)
