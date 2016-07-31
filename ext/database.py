from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


class DataBaseURIError(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SQLAlchemy:
    def __init__(self):
        self.engine = None
        self.session = None
        self.Model = declarative_base()

    def init_app(self, app):
        if not app.db_uri:
            raise DataBaseURIError('请指定数据库 URI')
        self.engine = create_engine(app.db_uri)
        self.session = scoped_session(sessionmaker(bind=self.engine))
        app.db = self

    def create_all(self):
        self.Model.metadata.create_all(self.engine)

    def drop_all(self):
        self.Model.metadata.drop_all(self.engine)


db = SQLAlchemy()
