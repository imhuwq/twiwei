import uuid

from tornado.web import Application, RequestHandler
from app.models.main import User


class Tornado(Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = None
        self.session = None


class BaseHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            self.user_id = user_id.decode()
        else:
            self.user_id = str(uuid.uuid4().int)
            self.set_secure_cookie("user_id", self.user_id)
        self.session_cache = self.application.session.get(self.user_id)

        self.query = self.db.session.query

    @property
    def db(self):
        return self.application.db

    @property
    def session(self):
        return self.session_cache

    @session.setter
    def session(self, **kwargs):
        self.session_cache = self.application.session.set(self.user_id, **kwargs)

    def get_current_user(self):
        if not self.user_id:
            return None
        return self.query(User).get(int(self.user_id))

    def login(self, user):
        self.application.session.clr(self.user_id)
        self.clear_all_cookies()
        self.user_id = str(user.c_id)
        self.set_secure_cookie("user_id", self.user_id)
