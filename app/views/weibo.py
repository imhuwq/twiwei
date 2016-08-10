from datetime import datetime, timedelta

from tornado.escape import json_encode
from tornado.web import authenticated
from tornado.gen import coroutine
from dateutil import parser

from ext.application import BaseHandler
from ext.clients import Twitter, Weibo
from ..models.main import User

weibo = Weibo()


class RetwMessageHandler(BaseHandler):
    @coroutine
    def post(self):
        user = self.current_user
        wei_id = self.get_argument('id')
        text = self.get_argument('reply')
        if user and wei_id:
            result = yield weibo.repost_message(user.c_wei_token, wei_id=wei_id,
                                                text=text)
            if result:
                self.cache.clear()
                return self.write(json_encode({'status': 200}))

        return self.write(json_encode({'status': 500, 'msg': '操作失败'}))


handlers = [
    (r"/weibo/retw_msg", RetwMessageHandler)
]
