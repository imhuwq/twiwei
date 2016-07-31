import os

from ext.database import SQLAlchemy
from ext.session import SessionManager
from ext.application import Tornado

from config import settings, DB_URI, BASE_DIR
from app.views import handlers


class ConfigurationError(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


session = SessionManager()
db = SQLAlchemy()


def create_app(mode='develop'):
    if mode == 'product':
        app = Tornado(
            handlers=handlers,
            **settings
        )
        app.db_uri = DB_URI
    elif mode == 'develop':
        app = Tornado(
            handlers=handlers,
            debug=True,
            **settings
        )
        db_name = 'develop.sqlite'
        app.db_uri = 'sqlite:///' + os.path.join(BASE_DIR, db_name)
    elif mode == 'test':
        app = Tornado(
            handlers=handlers,
            **settings
        )
        db_name = 'test.sqlite'
        app.db_uri = 'sqlite:///' + os.path.join(BASE_DIR, db_name)
    else:
        raise ConfigurationError('运行模式只能在 develop/test/product 三选一')
    session.init_app(app)
    db.init_app(app)
    return app
