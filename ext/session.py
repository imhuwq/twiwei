import tornadis
import json


class Session:
    def __init__(self, app=None):
        self.app = app
        self.client = tornadis.Client(host="localhost", port=6379, autoconnect=True)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.session = self

    def get(self, user_id):
        return self.client.call("get", 'session_%s' % user_id)

    def set(self, user_id, **kwargs):
        items = json.loads(self.get(user_id))
        items.update(**kwargs)
        new_items = json.dumps(items)
        self.client.call("set", 'session_%s' % user_id, new_items)
        return items
