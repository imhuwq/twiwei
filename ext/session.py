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

    @tornado.gen.coroutine
    def get(self, user_id):
        data = yield self.client.call("get", 'session_%s' % user_id)
        if data:
            return json.loads(data)
        return dict()

    @tornado.gen.coroutine
    def set(self, user_id, **kwargs):
        items = self.get(user_id)
        items.update(**kwargs)
        new_items = json.dumps(items)
        yield self.client.call("set", 'session_%s' % user_id, new_items)
        return items

    @tornado.gen.coroutine
    def clr(self, user_id):
        yield self.client.call("del", 'session_%s' % user_id)


session = Session()
