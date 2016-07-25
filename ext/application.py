import uuid

from tornado.gen import coroutine
from tornado.web import Application, RequestHandler

from .session import Session, Cache
from app.models.main import User


class Tornado(Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 与 SQLAlchemy 的连接， 用于数据库操作
        self.db = None

        # 与 redis 的连接， 用于session缓存
        # cookie中只保存 user_id， 其余信息都保存在 redis
        self.session = None


class BaseHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db = self.application.db
        self.query = self.application.db.session.query
        self.session = Session(self)
        self.cache = Cache(self)
        self.sessions = dict()

        self.user_id = None

    @coroutine
    def prepare(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            self.user_id = user_id.decode()
        else:
            self.set_random_user_cookie()

        self.sessions = yield self.session.get_all()

    def set_random_user_cookie(self):
        self.user_id = str(uuid.uuid4().int)
        self.set_secure_cookie("user_id", self.user_id)

    # 只要 cookie 中含有有效的 user_id (已加密， 未篡改， 未过期)
    # 并且在数据库中能找到对应的用户数据
    # 就能保证目前处于已登陆状态
    def get_current_user(self):
        return self.query(User).get(int(self.user_id))

    # 登陆用户：
    # 1. 把当前保存的 session 信息转移到目标用户处
    # 2. 更新 handler 的 current_user 和 user_id 信息
    # 3. 把 cookie 中的 user_id 修改成目标用户的 id
    def login(self, user):
        if not self.current_user:
            self.session.rename(str(user.c_id))
            self.current_user = user
            self.user_id = str(user.c_id)
            self.set_secure_cookie("user_id", self.user_id)

    # 注销用户:
    # 1. 删除 session 信息
    # 2. 重新生成匿名用户cookie
    def logout(self):
        if self.current_user:
            self.session.delete()
            self.set_random_user_cookie()
        self.redirect('/')
