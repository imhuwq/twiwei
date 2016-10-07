from tornado.escape import json_encode
from tornado.gen import coroutine

from ext.application import BaseHandler
from ext.clients import Weibo

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


class ReplyMessageHandler(BaseHandler):
    @coroutine
    def post(self):
        user = self.current_user
        wei_id = self.get_argument('id')
        text = self.get_argument('reply')
        if user and wei_id:
            result = yield weibo.reply_message(user.c_wei_token, wei_id, text)

            if result:
                return self.write(json_encode({'status': 200}))

        return self.write(json_encode({'status': 500, 'msg': '操作失败'}))


class GetMessageReplyHnadler(BaseHandler):
    @coroutine
    def get(self):
        wei_id = self.get_argument('id')
        since_id = self.get_argument('since_id', 0)
        max_id = self.get_argument('max_id', 0)
        user = self.current_user
        if user and wei_id:
            result = yield weibo.get_weibo_replies(user.c_wei_token, wei_id, since_id, max_id, count=20)
            if result:
                return self.write(json_encode({'status': 200, 'replies': result}))
        return self.write(json_encode({'status': 500, 'msg': '操作失败'}))


handlers = [
    (r"/weibo/retw_msg", RetwMessageHandler),
    (r"/weibo/reply_msg", ReplyMessageHandler),
    (r"/weibo/reply_list", GetMessageReplyHnadler),
]
