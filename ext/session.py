import tornadis
import json

import tornado.gen


class Session:
    def __init__(self, app=None):
        self.app = app
        self.client = tornadis.Client(host="localhost", port=6379, autoconnect=True)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.session = self


class HandlerSession:
    def __init__(self, handler):
        self.handler = handler
        self.client = handler.application.session.client

    @tornado.gen.coroutine
    def get_all(self):
        items = yield self.client.call("get", 'session_%s' % self.handler.user_id)
        if items:
            return json.loads(items.decode())
        return dict()

    @tornado.gen.coroutine
    def get(self, key):
        items = yield self.get_all()
        if items:
            return items.get(key)
        return None

    @tornado.gen.coroutine
    def set(self, **kwargs):
        self.handler.sessions.update(**kwargs)
        new_items = json.dumps(self.handler.sessions)
        yield self.client.call("set", 'session_%s' % self.handler.user_id, new_items)

    @tornado.gen.coroutine
    def rename(self, new_key):
        items = yield self.get(self.handler.user_id)
        if items:
            self.handler.sessions = items
            yield self.client.call("rename", 'session_%s' % self.handler.user_id, 'session_%s' % new_key)

    @tornado.gen.coroutine
    def delete(self):
        self.handler.sessions = dict()
        yield self.client.call("del", 'session_%s' % self.handler.user_id)


session = Session()
