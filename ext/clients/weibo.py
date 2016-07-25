from datetime import datetime
import json

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import url_concat
from tornado.gen import coroutine

from config import WEI_CLIENT_ID, WEI_CLIENT_SECRET, WEI_ADMIN_TOKEN


class Weibo(object):
    def __init__(self):
        AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        self.client = AsyncHTTPClient()

        # 开发者 token
        self.client_id = WEI_CLIENT_ID
        self.client_secret = WEI_CLIENT_SECRET
        self.admin_token = WEI_ADMIN_TOKEN

        # oauth 相关 url
        self.oauth2_url = 'https://api.weibo.com/oauth2/authorize?' \
                          'client_id=%s&' \
                          'response_type=code&' \
                          'redirect_uri=twiwei.com/oauth2/weibo/access_token/' % self.client_id
        self.access_token_url = 'https://api.weibo.com/oauth2/access_token'

        # 时间线相关 url
        self.user_home_url = 'https://api.weibo.com/2/statuses/home_timeline.json'
        self.public_url = 'https://api.weibo.com/2/statuses/public_timeline.json'

        # 用户操作相关 url
        self.like_weibo_url = 'https://api.weibo.com/2/favorites/create.json'
        self.unlike_weibo_url = 'https://api.weibo.com/2/favorites/destroy.json'
        self.get_replies_url = 'https://api.weibo.com/2/comments/show.json'

        # 用户信息相关 url
        self.user_info_url = 'https://api.weibo.com/2/users/show.json'
        self.liked_url = 'https://api.weibo.com/2/favorites/ids.json'

    #######################
    # 以下是辅助函数        #
    ######################
    @staticmethod
    def extract_raw_status(data):
        raw_statuses = data.get('statuses', [])
        pro_statuses = []
        for r_s in raw_statuses:
            p_s = dict()

            p_s['time'] = datetime.strptime(r_s.get('created_at'), '%a %b %d %H:%M:%S %z %Y').isoformat()
            p_s['text'] = r_s.get('text')

            p_s['imgs'] = []
            thumb_pics = r_s.get('pic_urls')
            for thumb_pic in thumb_pics:
                thumb = thumb_pic.get('thumbnail_pic')
                middl = thumb.replace('/thumbnail/', '/bmiddle/')
                origi = thumb.replace('/thumbnail/', '/large/')
                p_s['imgs'].append({
                    'thumb': thumb,
                    'middl': middl,
                    'origi': origi
                })

            u = r_s.get('user')
            p_s['writer'] = u.get('name')
            p_s['profile'] = u.get('profile_image_url')
            p_s['type'] = 'weibo'
            p_s['id'] = r_s.get('id')
            p_s['liked'] = r_s.get('liked', False)

            pro_statuses.append(p_s)

        return pro_statuses

    @staticmethod
    def gen_requests(method='GET', url=None, **kwargs):
        url = url_concat(url, kwargs)
        request = HTTPRequest(method=method, url=url, allow_nonstandard_methods=True)
        return request

    #######################
    # 以下是 oauth 相关函数 #
    ######################
    @coroutine
    def access_token(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': 'twiwei.com/oauth2/weibo/access_token/',
            'code': code
        }
        request = self.gen_requests('POST', self.access_token_url, **params)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return response

    #######################
    # 以下是用户信息相关函数 #
    ######################
    @coroutine
    def get_user_info(self, token, uid):

        params = {
            'access_token': token,
            'uid': uid
        }
        request = self.gen_requests('GET', self.user_info_url, **params)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return {
            'name': response.get('name') + '@weibo',
            'gender': response.get('gender'),
            'avatar': response.get('profile_image_url')
        }

    @coroutine
    def get_liked_msg(self, token):
        params = {
            'access_token': token,
            'count': 10000
        }
        request = self.gen_requests('GET', self.liked_url, **params)
        response = yield self.client.fetch(request)
        liked_msgs = json.loads(response.body.decode()).get("favorites", [])
        ids = [msg.get('status') for msg in liked_msgs]
        return ids

    #######################
    # 以下是时间线相关函数   #
    ######################
    @coroutine
    def get_user_timeline(self, token, **kwargs):
        if token:
            params = {
                'access_token': token
            }
            for key, value in kwargs.items():
                params[key] = value
            request = self.gen_requests('GET', self.user_home_url, **params)
            response = yield self.client.fetch(request)
            response = json.loads(response.body.decode())
            statuses = self.extract_raw_status(response)
            return statuses

    @coroutine
    def get_pub_timeline(self, token, count=20, page=1):

        params = {
            'access_token': token,
            'count': count,
            'page': page
        }

        request = self.gen_requests('GET', self.public_url, **params)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        statuses = self.extract_raw_status(response)
        return statuses

    #######################
    # 以下是用户操作相关函数 #
    ######################
    @coroutine
    def like_this_weibo(self, access_token, wei_id):
        params = {
            'access_token': access_token,
            'id': wei_id
        }
        request = self.gen_requests('POST', self.like_weibo_url, **params)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return response.get('favorited')

    @coroutine
    def unlike_this_weibo(self, access_token, wei_id):
        params = {
            'access_token': access_token,
            'id': wei_id
        }
        request = self.gen_requests('POST', self.like_weibo_url, params=params)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return response.get('favorited')

    @coroutine
    def get_weibo_replies(self, access_token, wei_id, since_id=0, max_id=0, **kwargs):
        request = self.gen_requests('GET', self.get_replies_url, access_token=access_token,
                                    wei_id=wei_id, since_id=since_id, max_id=max_id, **kwargs)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
