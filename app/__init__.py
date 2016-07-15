from ext.application import Tornado
from ext.database import SQLAlchemy
from ext.session import Session

from config import settings
from .views.main import handlers as mai_handlers

db = SQLAlchemy()
session = Session()

handlers = []

handlers.extend(mai_handlers)


def create_app(debug=True):
    app = Tornado(
        handlers=handlers,
        debug=debug,
        **settings
    )
    db.init_app(app)
    session.init_app(app)
    return app

