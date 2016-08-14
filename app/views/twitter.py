from datetime import datetime, timedelta

from tornado.escape import json_encode
from tornado.web import authenticated
from tornado.gen import coroutine
from dateutil import parser

from ext.application import BaseHandler
from ext.clients import Twitter, Weibo
from ..models.main import User

twitter = Twitter()


class LikeHandler(BaseHandler):
    @coroutine
    def post(self):
        user = self.current_user
        twi_id = self.get_argument('id')
        if user and twi_id:
            result = yield twitter.like_this_msg(user.c_twi_token, user.c_twi_secret, msg_id=twi_id)
            if result:
                cache = yield self.cache.get('twitter')
                if cache:
                    liked_msg = [msg for msg in cache if msg['id'] == twi_id][0]
                    liked_msg['liked'] = True
                    self.cache.set(ttl=0, twitter=cache)
                return self.write(json_encode({'status': 200, 'msg': ''}))
            else:
                return self.write(json_encode({'status': 500, 'msg': '操作失败！'}))
        return self.write(json_encode({'status': 400, 'msg': '无效的请求'}))


class UnLikeHandler(BaseHandler):
    @coroutine
    def post(self):
        user = self.current_user
        twi_id = self.get_argument('id')
        if user and twi_id:
            result = yield twitter.unlike_this_msg(user.c_twi_token, user.c_twi_secret, msg_id=twi_id)
            if result is False:
                cache = yield self.cache.get('twitter')
                if cache:
                    liked_msg = [msg for msg in cache if msg['id'] == twi_id][0]
                    liked_msg['liked'] = False
                    self.cache.set(ttl=0, twitter=cache)
                return self.write(json_encode({'status': 200, 'msg': ''}))
            else:
                return self.write(json_encode({'status': 500, 'msg': '操作失败！'}))
        return self.write(json_encode({'status': 400, 'msg': '无效的请求'}))


class RetwMessageHandler(BaseHandler):
    @coroutine
    def post(self):
        user = self.current_user
        twi_id = self.get_argument('id')
        screen_name = self.get_argument('screen_name')
        reply = self.get_argument('reply')
        if reply:
            reply_text = 'RT @%s: %s https://twitter.com/%s/statuses/%s' % (screen_name, reply, screen_name, twi_id)
        else:
            reply_text = 'RT @%s https://twitter.com/%s/statuses/%s' % (screen_name, screen_name, twi_id)
        if user and twi_id:
            result = yield twitter.retw_with_comment(user.c_twi_token, user.c_twi_secret, reply_text)

            if result:
                self.cache.clear()
                return self.write(json_encode({'status': 200}))

        return self.write(json_encode({'status': 500, 'msg': '操作失败'}))


class ReplyMessageHandler(BaseHandler):
    @coroutine
    def post(self):
        user = self.current_user
        twi_id = self.get_argument('id')
        screen_name = self.get_argument('screen_name')
        reply = self.get_argument('reply')
        reply_text = '@%s: %s' % (screen_name, reply)

        if user and twi_id:
            result = yield twitter.reply_message(user.c_twi_token, user.c_twi_secret, twi_id, reply_text)

            if result:
                return self.write(json_encode({'status': 200}))

        return self.write(json_encode({'status': 500, 'msg': '操作失败'}))


handlers = [
    (r"/twitter/like_msg", LikeHandler),
    (r"/twitter/unlike_msg", UnLikeHandler),
    (r"/twitter/retw_msg", RetwMessageHandler),
    (r"/twitter/reply_msg", ReplyMessageHandler)
]

# todo: session expire mechanism
# todo: momoko async db pool
# todo: transfer from sql data to json in postgresql
