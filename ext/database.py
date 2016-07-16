from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from config import DB_URI


class SQLAlchemy:
    def __init__(self, app=None):
        self.engine = create_engine(DB_URI)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        self.Model = declarative_base()
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.db = self


db = SQLAlchemy()
