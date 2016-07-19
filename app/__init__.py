from ext.database import db
from ext.session import session
from ext.application import Tornado

from config import settings
from .views import handlers


def create_app(debug=True):
    app = Tornado(
        handlers=handlers,
        debug=debug,
        **settings
    )
    db.init_app(app)
    session.init_app(app)
    return app
