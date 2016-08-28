from datetime import datetime, timedelta

from tornado.escape import json_encode
from tornado.web import authenticated
from tornado.gen import coroutine
from dateutil import parser

from ext.application import BaseHandler
from ext.clients import Twitter, Weibo
from app.models.main import User

weibo = Weibo()
twitter = Twitter()


class IndexHandler(BaseHandler):
    def get(self):
        return self.render('main/index.html')


class LoadHomeHandler(BaseHandler):
    @coroutine
    def get(self):
        user = self.current_user

        statuses = []
        if user:

            data_wei, data_twi = yield [self.cache.get('weibo'), self.cache.get('twitter')]

            if data_wei:
                data_wei = data_wei[0:20]
            else:
                token = user.c_wei_token
                data_wei = yield weibo.get_user_timeline(token)
                self.cache.set(weibo=data_wei)
            if data_wei:
                self.set_cookie('wei_since', str(data_wei[0]['id']))
                self.set_cookie('wei_max', str(data_wei[-1]['id']))
                statuses.extend(data_wei)

            if data_twi:
                data_twi = data_twi[0:20]
            else:
                data_twi = yield twitter.get_user_timeline(user.c_twi_token,
                                                           user.c_twi_secret)
                self.cache.set(twitter=data_twi)
            if data_twi:
                self.set_cookie('twi_since', str(data_twi[0]['id']))
                self.set_cookie('twi_max', str(data_twi[-1]['id']))
                statuses.extend(data_twi)
            statuses = sorted(statuses, key=lambda s: parser.parse(s.get('time')), reverse=True)

        elif weibo.admin_token:
            data = yield self.cache.get('anonymous', is_anonymous=True)
            if not data:
                data = yield weibo.get_pub_timeline(weibo.admin_token)
                self.cache.set(anonymous=data, is_anonymous=True)
            statuses.extend(data)
        self.write(json_encode(
            {
                'status': 200,
                'msg': '',
                'content': statuses
            }
        ))


class LoadMoreHandler(BaseHandler):
    @coroutine
    def get(self):
        user = self.current_user

        statuses = []
        if user:
            wei_max = int(self.get_cookie('wei_max'))
            data_wei = yield self.cache.get('weibo')
            data_wei = [data for data in data_wei if int(data.get('id')) < wei_max][0:20]
            if not data_wei:
                data_wei = yield weibo.get_user_timeline(user.c_wei_token,
                                                         max_id=wei_max)
                data_wei = data_wei[1:]
                self.cache.add('weibo', data_wei)
                self.set_cookie('wei_max', str(data_wei[-1]['id']))
            statuses.extend(data_wei)

            twi_max = int(self.get_cookie('twi_max'))
            data_twi = yield self.cache.get('twitter')
            data_twi = [data for data in data_twi if int(data.get('id')) < twi_max][0:20]
            if not data_twi:
                data_twi = yield twitter.get_user_timeline(user.c_twi_token,
                                                           user.c_twi_secret,
                                                           max_id=twi_max)
                data_twi = data_twi[1:]
                self.cache.add('twitter', data_twi)
                self.set_cookie('twi_max', str(data_twi[-1]['id']))
            statuses.extend(data_twi)

            statuses = sorted(statuses, key=lambda s: parser.parse(s.get('time')), reverse=True)

            return self.write(json_encode(
                {
                    'status': 200,
                    'msg': '',
                    'content': statuses
                }
            ))
        return self.write(json_encode(
            {
                'status': 400,
                'msg': '登陆后再使用该功能'
            })
        )


class LoginHandler(BaseHandler):
    @coroutine
    def get(self):
        site = self.get_argument('site', default='local')
        if site == 'weibo':
            return self.redirect(weibo.oauth2_url)

        elif site == 'twitter':
            oauth_token, oauth_token_secret = yield twitter.request_token()

            self.session.set(oauth_token=oauth_token,
                             oauth_token_secret=oauth_token_secret)

            return self.redirect(twitter.authorize_url(oauth_token))

        return self.render('main/login.html')


class LogoutHandler(BaseHandler):
    def get(self):
        self.logout()


class TwitterCallbackHandler(BaseHandler):
    @coroutine
    def get(self):
        user = self.current_user
        oauth_token = self.get_argument('oauth_token', default=None)
        oauth_verifier = self.get_argument('oauth_verifier', default=None)
        previous_oauth_token = yield self.session.get('oauth_token')
        self.session.delete()
        if oauth_token == previous_oauth_token:
            data = yield twitter.access_token(oauth_token, oauth_verifier)
            token = data.get('oauth_token')
            token_secret = data.get('oauth_token_secret')
            twi_id = data.get('user_id')

            # 用户已经登陆， 说明是用weibo连接twitter账户
            if user:
                old_user = self.query(User).filter_by(c_twi_id=twi_id).first()
                update_fields = {
                    'c_twi_id': twi_id,
                    'c_twi_token': token,
                    'c_twi_token_secret': token_secret
                }

                if old_user:
                    User.merge_user(old_user, user, update_fields)
                else:
                    user.update_fields(update_fields)
                return self.redirect('/account/')

            # 用户没有登陆，说明是直接使用 twitter 登陆
            else:
                user = self.query(User).filter_by(c_twi_id=twi_id).first()
                if not user:
                    user = User(c_twi_id=twi_id,
                                c_join=datetime.utcnow())
                    self.db.session.add(user)
                user.c_twi_token = token
                user.c_twi_secret = token_secret
                self.db.session.commit()

                self.login(user)

                return self.redirect('/')


class WeiboCallbackHandler(BaseHandler):
    @coroutine
    def get(self):
        user = self.current_user
        code = self.get_argument('code', default=None)
        data = yield weibo.access_token(code)
        token = data.get('access_token')
        expire = data.get('expires_in')
        wei_id = data.get('uid')

        # 用户已经登陆， 说明是在用twitter账户链接weibo账户
        if user:
            old_user = self.query(User).filter_by(c_wei_id=wei_id).first()
            update_fields = {
                'c_wei_id': wei_id,
                'c_wei_token': token,
                'c_wei_token_expire': datetime.utcnow() + timedelta(0, int(expire) - 60),
            }

            if old_user:
                User.merge_user(old_user, user, update_fields)
            else:
                user.update_fields(update_fields)
            return self.redirect('/account/')

        # 用户没有登陆， 说明是直接用微博账户登录
        else:
            user = self.query(User).filter_by(c_wei_id=wei_id).first()
            if not user:
                user = User(c_wei_id=wei_id,
                            c_join=datetime.utcnow())
                self.db.session.add(user)
            user.c_wei_token = token
            user.c_wei_expire = datetime.utcnow() + timedelta(0, int(expire) - 60)

            self.db.session.commit()

            self.login(user)

            return self.redirect('/')


class UserAccountHandler(BaseHandler):
    @authenticated
    def get(self):
        return self.render('main/account.html')


class UserPageHandler(BaseHandler):
    @coroutine
    def get(self, site, screen_name):
        return self.write('%s from %s' % (screen_name, site))


class TopicPageHandler(BaseHandler):
    @coroutine
    def get(self, site, topic):
        return self.write('%s from %s' % (topic, site))


handlers = [
    (r"/", IndexHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/account/", UserAccountHandler),
    (r"/load_home", LoadHomeHandler),
    (r"/load_more", LoadMoreHandler),
    (r"/oauth2/twitter/access_token/", TwitterCallbackHandler),
    (r"/oauth2/weibo/access_token/", WeiboCallbackHandler),
    (r"/user/(.*?)/(.*?)", UserPageHandler),
    (r"/topic/(.*?)/(.*?)", UserPageHandler)
]
