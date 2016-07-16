from ext.database import db
from ext.session import session
from ext.application import Tornado

from config import settings
from .views.main import handlers as mai_handlers

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
