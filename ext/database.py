from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Query, scoped_session

from config import db_uri


class SQLAlchemy:
    def __init__(self, app=None):
        self.engine = create_engine(db_uri)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.db = self.session
