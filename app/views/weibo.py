from datetime import datetime, timedelta

from tornado.escape import json_encode
from tornado.web import authenticated
from tornado.gen import coroutine
from dateutil import parser

from ext.application import BaseHandler
from ext.clients import Twitter, Weibo
from ..models.main import User

weibo = Weibo()
twitter = Twitter()


class LikeHandler(BaseHandler):
    @coroutine
    def post(self):
        user = self.current_user
        wei_id = self.get_argument('id')
        if user and wei_id:
            result = yield weibo.like_this_weibo(self.current_user.c_wei_token, wei_id)
            if result:
                self.write(json_encode({'status': 200, 'msg': ''}))
            else:
                self.write(json_encode({'status': 500, 'msg': '操作失败！'}))
        self.write(json_encode({'status': 400, 'msg': '无效的请求'}))



class UnLikeHandler(BaseHandler):
    @coroutine
    def get(self):
        user = self.current_user
        wei_id = self.get_argument('id')
        if user and wei_id:
            result = yield weibo.unlike_this_weibo(self.current_user.c_wei_token, wei_id)
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
    (r"/weibo/like_msg", LikeHandler),
    (r"/weibo/unlike_msg", UnLikeHandler),
    (r"/weibo/reply", ReplyHandler),
    (r"/weibo/rewei", ReWeiHandler),
]

# todo: session expire mechanism
# todo: momoko async db pool
# todo: store max_id and since id to session instead of db
# todo: transfer from sql data to json in postgresql
