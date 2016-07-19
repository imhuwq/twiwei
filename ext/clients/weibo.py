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

        self.client_id = WEI_CLIENT_ID
        self.client_secret = WEI_CLIENT_SECRET
        self.admin_token = WEI_ADMIN_TOKEN

        self.oauth2_url = 'https://api.weibo.com/oauth2/authorize?' \
                          'client_id=%s&' \
                          'response_type=code&' \
                          'redirect_uri=twiwei.com/oauth2/weibo/access_token/' % self.client_id
        self.access_token_url = 'https://api.weibo.com/oauth2/access_token'

        self.user_info_url = 'https://api.weibo.com/2/users/show.json'
        self.user_home_url = 'https://api.weibo.com/2/statuses/home_timeline.json'
        self.public_url = 'https://api.weibo.com/2/statuses/public_timeline.json'

    @staticmethod
    def gen_requests(method='GET', url=None, params=None):
        url = url_concat(url, params)
        request = HTTPRequest(method=method, url=url, allow_nonstandard_methods=True)
        return request

    @coroutine
    def access_token(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': 'twiwei.com/oauth2/weibo/access_token/',
            'code': code
        }
        request = self.gen_requests('POST', self.access_token_url, params)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return response

    @coroutine
    def get_user_info(self, token, uid):

        params = {
            'access_token': token,
            'uid': uid
        }
        request = self.gen_requests('GET', self.user_info_url, params)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return {
            'name': response.get('name') + '@weibo',
            'gender': response.get('gender'),
            'avatar': response.get('profile_image_url')
        }

    @coroutine
    def get_user_timeline(self, token, valid_user=True, **kwargs):
        if valid_user:
            params = {
                'access_token': token
            }
            for key, value in kwargs.items():
                params[key] = value
            request = self.gen_requests('GET', self.user_home_url, params)
            response = yield self.client.fetch(request)
            response = json.loads(response.body.decode())
            return response
        return []

    @coroutine
    def get_pub_timeline(self, token, count=20, page=1):

        params = {
            'access_token': token,
            'count': count,
            'page': page
        }

        request = self.gen_requests('GET', self.public_url, params)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return response

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
            p_s['type'] = 'wei'
            p_s['id'] = r_s.get('id')

            pro_statuses.append(p_s)

        return pro_statuses
