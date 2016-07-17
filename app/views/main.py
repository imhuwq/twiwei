from datetime import datetime, timedelta

from tornado.escape import json_encode
from tornado.web import authenticated
from tornado.gen import coroutine

from ext.application import BaseHandler
from ..clients import Twitter, Weibo
from ..models.main import User

weibo = Weibo()
twitter = Twitter()


class IndexHandler(BaseHandler):
    def get(self):
        # user = self.current_user
        # statuses = []
        # if user:
        #     if user.c_wei_id:
        #         data = weibo.get_user_timeline(user.c_wei_token)
        #         statuses.extend(weibo.extract_raw_status(data))
        #         user.c_wei_since = statuses[0]['id']
        #         user.c_wei_max = statuses[-1]['id']
        #     if user.c_twi_id:
        #         data = twitter.get_user_timeline(user.c_twi_token, user.c_twi_secret)
        #         statuses.extend(twitter.extract_raw_statuses(data))
        #         user.c_twi_since = statuses[0]['id']
        #         user.c_twi_max = statuses[-1]['id']
        #     self.db.session.commit()
        # elif weibo.admin_token:
        #     raw = weibo.get_pub_timeline(weibo.admin_token)
        #     status = weibo.extract_raw_status(raw)
        #     statuses.extend(status)
        #
        # if statuses:
        #     statuses = sorted(statuses, key=lambda s: s.get('time'), reverse=True)
        #     context = {'statuses': statuses}
        return self.render('main/index.html')


class LoadHomeHandler(BaseHandler):
    def get(self):
        user = self.current_user

        statuses = []
        if user:
            if user.c_wei_id:
                data = weibo.get_user_timeline(user.c_wei_token, max_id=user.c_wei_max)
                statuses.extend(weibo.extract_raw_status(data)[1:-1])
                user.c_wei_since = statuses[0]['id']
                user.c_wei_max = statuses[-1]['id']
            if user.c_twi_id:
                data = twitter.get_user_timeline(user.c_twi_token, user.c_twi_secret, max_id=user.c_twi_max)
                if data:
                    statuses.extend(twitter.extract_raw_statuses(data)[1:-1])
                    user.c_twi_since = statuses[0]['id']
                    user.c_twi_max = statuses[-1]['id']

            self.db.session.commit()
            statuses = sorted(statuses, key=lambda s: s.get('time'), reverse=True)

        elif weibo.admin_token:
            raw = weibo.get_pub_timeline(weibo.admin_token)
            status = weibo.extract_raw_status(raw)
            statuses.extend(status)

        return self.write(json_encode(
            {
                'status': 200,
                'msg': '',
                'content': statuses
            }
        ))


class LoadMoreHandler(BaseHandler):
    def get(self):
        user = self.current_user

        statuses = []
        if user:
            if user.c_wei_id:
                data = weibo.get_user_timeline(user.c_wei_token, max_id=user.c_wei_max)
                statuses.extend(weibo.extract_raw_status(data)[1:-1])
                user.c_wei_max = statuses[-1]['id']
            if user.c_twi_id:
                data = twitter.get_user_timeline(user.c_twi_token, user.c_twi_secret, max_id=user.c_twi_max)
                statuses.extend(twitter.extract_raw_statuses(data)[1:-1])
                user.c_twi_max = statuses[-1]['id']
            self.db.session.commit()
            statuses = sorted(statuses, key=lambda s: s.get('time'), reverse=True)
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
    def get(self):
        site = self.get_argument('site', default='local')
        if site == 'weibo':
            return self.redirect(weibo.oauth2_url)

        elif site == 'twitter':
            oauth_token, oauth_token_secret = twitter.request_token()

            self.session.set(oauth_token=oauth_token,
                             oauth_token_secret=oauth_token_secret)

            return self.redirect(twitter.authorize_url)

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
        if oauth_token == previous_oauth_token:
            data = twitter.access_token(oauth_token, oauth_verifier)
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
    def get(self):
        user = self.current_user
        code = self.get_argument('code', default=None)
        data = weibo.access_token(code)
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
            return self.redirect('/account')

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


handlers = [
    (r"/", IndexHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/account/", UserAccountHandler),
    (r"/load_home", LoadHomeHandler),
    (r"/load_more", LoadMoreHandler),
    (r"/oauth2/twitter/access_token/", TwitterCallbackHandler),
    (r"/oauth2/weibo/access_token/", WeiboCallbackHandler)
]
