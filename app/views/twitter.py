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
        wei_id = self.get_argument('id')
        if user and wei_id:
            result = yield twitter.like_this_msg(user.c_twi_token, user.c_twi_secret, msg_id=wei_id)
            if result:
                self.write(json_encode({'status': 200, 'msg': ''}))
            else:
                self.write(json_encode({'status': 500, 'msg': '操作失败！'}))
        self.write(json_encode({'status': 400, 'msg': '无效的请求'}))


class UnLikeHandler(BaseHandler):
    @coroutine
    def post(self):
        user = self.current_user
        wei_id = self.get_argument('id')
        if user and wei_id:
            result = yield twitter.unlike_this_msg(user.c_twi_token, user.c_twi_secret, msg_id=wei_id)
            if result is False:
                self.write(json_encode({'status': 200, 'msg': ''}))
            else:
                self.write(json_encode({'status': 500, 'msg': '操作失败！'}))
        self.write(json_encode({'status': 400, 'msg': '无效的请求'}))


class ReplyHandler(BaseHandler):
    @coroutine
    def post(self):
        user = self.current_user


class ReWeiHandler(BaseHandler):
    pass


handlers = [
    (r"/twitter/like_msg", LikeHandler),
    (r"/twitter/unlike_msg", UnLikeHandler),
    (r"/twitter/reply", ReplyHandler),
    (r"/twitter/retw", ReWeiHandler),
]

# todo: session expire mechanism
# todo: momoko async db pool
# todo: transfer from sql data to json in postgresql
