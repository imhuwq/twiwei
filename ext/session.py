import tornadis
import json

import tornado.gen


class SessionManager:
    """ 与 app 绑定的 session client, 一个 app 一个 redis client"""

    def __init__(self, app=None):
        self.app = app
        self.client = tornadis.Client(host="localhost", port=6379, autoconnect=True)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.session = self


class Session:
    """ 与 handler 绑定的 session， 一个 handler 一个 session 对象， 公用一个 client"""

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
        items = self.handler.sessions
        if items:
            return items.get(key)
        return None

    @tornado.gen.coroutine
    def set(self, **kwargs):
        """ session 默认的 TTL 是 1 天 """
        self.handler.sessions.update(kwargs)
        new_items = json.dumps(self.handler.sessions)
        yield self.client.call("set", 'session_%s' % self.handler.user_id, new_items, 'ex', 79200)

    @tornado.gen.coroutine
    def rename(self, new_key):
        """ 用户登陆后， 将未登录时的 session 数据转移到用户的 session 中"""
        items = yield self.get(self.handler.user_id)
        if items:
            self.handler.sessions = items
            yield self.client.call("rename", 'session_%s' % self.handler.user_id, 'session_%s' % new_key)

    @tornado.gen.coroutine
    def delete(self):
        """ 用户注销后， 删除所有 session 数据 """
        self.handler.sessions = dict()
        yield self.client.call("del", 'session_%s' % self.handler.user_id)


class Cache:
    """ cache 与 session 都是保存在 redis 中的缓存， session 保存用户关键信息，
    cache 保存 statuses， 避免短时间内重复请求， cache 的 TTL 为 3 min"""

    def __init__(self, handler):
        self.handler = handler
        self.client = handler.application.session.client

    @tornado.gen.coroutine
    def get_all(self, is_anonymous=False):
        if not is_anonymous:
            key = 'cache_%s' % self.handler.user_id
        else:
            key = 'cache_anonymous'

        items = yield self.client.call("get", key)
        if items:
            items = json.loads(items.decode())
            return items
        return dict()

    @tornado.gen.coroutine
    def get(self, key, is_anonymous=False):
        items = yield self.get_all(is_anonymous)
        return items.get(key, [])

    @tornado.gen.coroutine
    def set(self, is_anonymous=False, ttl=180, **kwargs):
        """因为在 redis 中使用 set 命令时会覆盖原有 TTL
           所以可以在更新时指定 TTL=0， 这样会在原有时间上加 1 秒"""
        if kwargs:
            if not is_anonymous:
                key = 'cache_%s' % self.handler.user_id
            else:
                key = 'cache_anonymous'
            items = yield self.get_all(is_anonymous)
            items.update(**kwargs)
            new_items = json.dumps(items)
            if ttl == 0:
                ttl = yield self.client.call('ttl', key)
                ttl += 1
            yield self.client.call("set", key, new_items, 'ex', ttl)

    @tornado.gen.coroutine
    def add(self, type, value):
        key = 'cache_%s' % self.handler.user_id
        items = yield self.get_all()
        old_value = items.setdefault(type, [])
        old_value.extend(value)
        new_items = json.dumps(items)
        ttl = yield self.client.call('ttl', key)
        yield self.client.call("set", key, new_items, 'ex', ttl + 10)

    @tornado.gen.coroutine
    def clear(self):
        key = 'cache_%s' % self.handler.user_id
        yield self.client.call('del', key)


session = SessionManager()
