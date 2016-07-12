from django.shortcuts import redirect

from datetime import datetime
from functools import wraps
from requests_oauthlib import OAuth1
import requests
import json
import re

from .models import User
from .api_keys import WEI_CLIENT_ID, WEI_CLIENT_SECRET, TWI_CLIENT_ID, TWI_CLIENT_SECRET


def login_required(func):
    from .views import site_login

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            return func(request, *args, **kwargs)
        return redirect(site_login)

    return wrapper


class WeiboAPI(object):
    def __init__(self):
        self.client_id = WEI_CLIENT_ID
        self.client_secret = WEI_CLIENT_SECRET

        self.oauth2_url = 'https://api.weibo.com/oauth2/authorize?' \
                          'client_id=%s&' \
                          'response_type=code&' \
                          'redirect_uri=twiwei.com/oauth2/weibo/access_token/' % self.client_id

        self.admin_token = User.objects.get(username='admin').wei_token

    def access_token(self, code):
        url = 'https://api.weibo.com/oauth2/access_token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': 'twiwei.com/oauth2/weibo/access_token/',
            'code': code
        }
        data = json.loads(requests.post(url, params).text)
        return data

    @staticmethod
    def get_user_info(token, uid):
        url = 'https://api.weibo.com/2/users/show.json'
        params = {
            'access_token': token,
            'uid': uid
        }
        data = json.loads(requests.get(url, params).text)
        return {
            'name': data.get('name') + '@weibo',
            'gender': data.get('gender'),
            'avatar': data.get('profile_image_url')
        }

    @staticmethod
    def get_user_timeline(token, count=20, page=1):
        url = 'https://api.weibo.com/2/statuses/home_timeline.json'
        params = {
            'access_token': token,
            'count': count,
            'page': page
        }
        data = json.loads(requests.get(url, params).text)
        return data

    @staticmethod
    def get_pub_timeline(token, count=20, page=1):
        url = 'https://api.weibo.com/2/statuses/public_timeline.json'
        params = {
            'access_token': token,
            'count': count,
            'page': page
        }
        data = json.loads(requests.get(url, params).text)
        return data

    @staticmethod
    def extract_raw_status(data):
        raw_statuses = data.get('statuses', [])
        pro_statuses = []
        for r_s in raw_statuses:
            p_s = dict()

            p_s['time'] = datetime.strptime(r_s.get('created_at'), '%a %b %d %H:%M:%S %z %Y')
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

            pro_statuses.append(p_s)

        return pro_statuses


class TwitterAPI(object):
    def __init__(self):
        self.client_key = TWI_CLIENT_ID
        self.client_secret = TWI_CLIENT_SECRET

        self.request_token_url = 'https://api.twitter.com/oauth/request_token'
        self.access_token_url = 'https://api.twitter.com/oauth/access_token'
        self.authorize_url = 'https://api.twitter.com/oauth/authorize'
        self.user_homeline_url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'

        self.oauth_callback = 'http://twiwei.com/oauth2/twitter/access_token/'

        self.oauth_token = ''
        self.oauth_token_secret = ''

    def request_token(self):
        oauth = OAuth1(self.client_key, client_secret=self.client_secret, callback_uri=self.oauth_callback)
        proxies = dict(http='socks5://127.0.0.1:1080',
                       https='socks5://127.0.0.1:1080')

        r = requests.post(url=self.request_token_url, auth=oauth, proxies=proxies)
        credentials = r.text.split('&')
        self.oauth_token = credentials[0].split('=')[1]
        self.oauth_token_secret = credentials[1].split('=')[1]

        return self.oauth_token, self.oauth_token_secret

    def get_authorize_url(self):
        return '%s?oauth_token=%s' % (self.authorize_url, self.oauth_token)

    def access_token(self, oauth_token, oauth_verifier):
        oauth = OAuth1(self.client_key,
                       client_secret=self.client_secret,
                       verifier=oauth_verifier,
                       resource_owner_key=oauth_token)
        proxies = dict(http='socks5://127.0.0.1:1080',
                       https='socks5://127.0.0.1:1080')
        data = requests.post(url=self.access_token_url, auth=oauth, proxies=proxies).text
        data = data.split('&')
        result = {}
        for d in data:
            k, v = d.split('=')
            result[k] = v

        return result

    def get_user_timeline(self, token, token_secret, **kwargs):
        oauth = OAuth1(self.client_key,
                       client_secret=self.client_secret,
                       resource_owner_key=token,
                       resource_owner_secret=token_secret)
        proxies = dict(http='socks5://127.0.0.1:1080',
                       https='socks5://127.0.0.1:1080')

        params = dict()
        for key, value in kwargs.items():
            params[key] = value
        data = requests.get(self.user_homeline_url, params, auth=oauth, proxies=proxies).text
        return json.loads(data)

    @staticmethod
    def extract_raw_statuses(data):
        statuses = []
        for d in data:
            status = dict()
            status['writer'] = d.get('user').get('name')
            status['text'] = re.sub(r'https://t.co/.*', '', d.get('text', ''))
            status['profile'] = d.get('user').get('profile_image_url')
            status['time'] = datetime.strptime(d.get('created_at'), '%a %b %d %H:%M:%S %z %Y')
            status['fav_count'] = d.get('favorite_count')
            status['imgs'] = []
            ext_ent = d.get('extended_entities')
            if ext_ent:
                for m in ext_ent.get('media'):
                    if m.get('type', None) == 'photo':
                        status['imgs'].append({
                            'origi': m.get('media_url')
                        })

            statuses.append(status)

        return statuses
