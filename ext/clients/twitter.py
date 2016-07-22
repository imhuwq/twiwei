import re
import json
from datetime import datetime

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import url_concat
from tornado.gen import coroutine
import pycurl
import requests
from requests import Request
from requests_oauthlib import OAuth1

from config import TWI_ADMIN_TOKEN_SECRET, TWI_ADMIN_TOKEN, TWI_CLIENT_ID, TWI_CLIENT_SECRET


class Twitter(object):
    def __init__(self):
        AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        self.client = AsyncHTTPClient()
        self.proxy_host = "127.0.0.1"
        self.proxy_port = 1080

        self.client_key = TWI_CLIENT_ID
        self.client_secret = TWI_CLIENT_SECRET

        self.request_token_url = 'https://api.twitter.com/oauth/request_token'
        self.access_token_url = 'https://api.twitter.com/oauth/access_token'
        self._authorize_url = 'https://api.twitter.com/oauth/authorize'

        self.oauth_callback = 'http://twiwei.com/oauth2/twitter/access_token/'

        self.admin_token = TWI_ADMIN_TOKEN
        self.admin_token_secret = TWI_ADMIN_TOKEN_SECRET

        self.user_homeline_url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
        self.public_url = ''

    @staticmethod
    def set_socks5_proxy(curl):
        curl.setopt(pycurl.PROXY, '127.0.0.1')
        curl.setopt(pycurl.PROXYPORT, 1080)
        curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)

    # 使用 requests_oauth 来生成 oauth1 header， 方便！
    def get_oauth_headers(self, method='GET', url='',
                          resource_owner_key=None,
                          resource_owner_secret=None,
                          callback_uri=None, verifier=None):
        oauth = OAuth1(client_key=self.client_key,
                       client_secret=self.client_secret,
                       resource_owner_key=resource_owner_key,
                       resource_owner_secret=resource_owner_secret,
                       callback_uri=callback_uri,
                       verifier=verifier)
        req = Request(method, url, auth=oauth).prepare()
        return req.headers

    # 用函数来生成 request， 主要是为了 tornado.httpclient 能自定义 header 和 proxy
    def gen_request(self, method='GET', url='',
                    resource_owner_key=None,
                    resource_owner_secret=None,
                    callback_uri=None, verifier=None,
                    use_proxy=True, **kwargs):
        if kwargs:
            url = url_concat(url, kwargs)
        headers = self.get_oauth_headers(method, url,
                                         resource_owner_key,
                                         resource_owner_secret,
                                         callback_uri, verifier)
        if use_proxy:
            request = HTTPRequest(url=url, method=method, headers=headers, allow_nonstandard_methods=True,
                                  prepare_curl_callback=self.set_socks5_proxy)
        else:
            request = HTTPRequest(url=url, method=method, headers=headers, allow_nonstandard_methods=True)
        return request

    @coroutine
    def request_token(self):
        request = self.gen_request('POST', self.request_token_url, callback_uri=self.oauth_callback)
        response = yield self.client.fetch(request)
        response = response.body.decode()
        credentials = response.split('&')
        oauth_token = credentials[0].split('=')[1]
        oauth_token_secret = credentials[1].split('=')[1]

        return oauth_token, oauth_token_secret

    def authorize_url(self, oauth_token):
        return '%s?oauth_token=%s' % (self._authorize_url, oauth_token)

    @coroutine
    def access_token(self, oauth_token, oauth_verifier):
        request = self.gen_request('POST', self.access_token_url,
                                   resource_owner_key=oauth_token,
                                   verifier=oauth_verifier)
        response = yield self.client.fetch(request)
        response = response.body.decode().split('&')
        result = {}
        for pair in response:
            k, v = pair.split('=')
            result[k] = v

        return result

    @coroutine
    def get_user_timeline(self, token, token_secret, valid_user=True, **kwargs):
        if valid_user:
            request = self.gen_request('GET', self.user_homeline_url,
                                       resource_owner_key=token,
                                       resource_owner_secret=token_secret,
                                       **kwargs)
            response = yield self.client.fetch(request)
            response = json.loads(response.body.decode())
            if type(response) != list:
                return []
            return response
        return []

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
                            'middl': m.get('media_url')
                        })
            status['type'] = 'twitter'
            status['id'] = d.get('id')

            statuses.append(status)

        return statuses
