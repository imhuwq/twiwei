from tornado.web import authenticated

from ext.application import BaseHandler


class IndexHandler(BaseHandler):
    def get(self):
        greeting = self.get_argument('greeting', 'Hello')
        self.write(greeting + self.user_id)


class LoginHandler(BaseHandler):
    def get(self):
        self.write("Login Page")


handlers = [
    (r"/", IndexHandler),
    (r"/", LoginHandler)
]
