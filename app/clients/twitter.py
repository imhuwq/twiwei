import requests
import re
from datetime import datetime

from requests_oauthlib import OAuth1

from config import TWI_ADMIN_TOKEN_SECRET, TWI_ADMIN_TOKEN, TWI_CLIENT_ID, TWI_CLIENT_SECRET


class Twitter(object):
    def __init__(self):
        self.client_key = TWI_CLIENT_ID
        self.client_secret = TWI_CLIENT_SECRET

        self.request_token_url = 'https://api.twitter.com/oauth/request_token'
        self.access_token_url = 'https://api.twitter.com/oauth/access_token'
        self._authorize_url = 'https://api.twitter.com/oauth/authorize'

        self.oauth_callback = 'http://twiwei.com/oauth2/twitter/access_token/'

        self.oauth_token = ''
        self.oauth_token_secret = ''

        self.admin_token = TWI_ADMIN_TOKEN
        self.admin_token_secret = TWI_ADMIN_TOKEN_SECRET

        self.user_homeline_url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
        self.public_url = ''

    def request_token(self):
        oauth = OAuth1(self.client_key, client_secret=self.client_secret, callback_uri=self.oauth_callback)
        proxies = dict(http='socks5://127.0.0.1:1080',
                       https='socks5://127.0.0.1:1080')

        r = requests.post(url=self.request_token_url, auth=oauth, proxies=proxies)
        credentials = r.text.split('&')
        self.oauth_token = credentials[0].split('=')[1]
        self.oauth_token_secret = credentials[1].split('=')[1]

        return self.oauth_token, self.oauth_token_secret

    @property
    def authorize_url(self):
        return '%s?oauth_token=%s' % (self._authorize_url, self.oauth_token)

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

        data = requests.get(self.user_homeline_url, params, auth=oauth, proxies=proxies).json()
        if type(data) != list:
            return []
        return data

    @staticmethod
    def extract_raw_statuses(data):
        statuses = []
        for d in data:
            status = dict()
            status['writer'] = d.get('user').get('name')
            status['text'] = re.sub(r'https://t.co/.*', '', d.get('text', ''))
            status['profile'] = d.get('user').get('profile_image_url')
            status['time'] = datetime.strptime(d.get('created_at'), '%a %b %d %H:%M:%S %z %Y').isoformat()
            status['fav_count'] = d.get('favorite_count')
            status['imgs'] = []
            ext_ent = d.get('extended_entities')
            if ext_ent:
                for m in ext_ent.get('media'):
                    if m.get('type', None) == 'photo':
                        status['imgs'].append({
                            'origi': m.get('media_url')
                        })
            status['type'] = 'twi'
            status['id'] = d.get('id')

            statuses.append(status)

        return statuses
