import os

from tornado.web import Application

from ext.database import db
from ext.session import session
from app.models.main import User
from config import settings, DB_URI, BASE_DIR
from app.views import handlers


class ConfigurationError(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Tornado(Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 与 SQLAlchemy 的连接， 用于数据库操作
        self.db = None
        self.db_uri = None

        # 与 redis 的连接， 用于session缓存
        # cookie中只保存 user_id， 其余信息都保存在 redis
        self.session = None


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
        app.db_uri = DB_URI
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
