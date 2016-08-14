import re
import json
from datetime import datetime

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import url_concat
from tornado.gen import coroutine
import pycurl
from requests import Request
from requests_oauthlib import OAuth1

from config import TWI_ADMIN_TOKEN_SECRET, TWI_ADMIN_TOKEN, TWI_CLIENT_ID, TWI_CLIENT_SECRET, USE_PROXY


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

        self.like_msg_url = 'https://api.twitter.com/1.1/favorites/create.json'
        self.unlike_msg_url = 'https://api.twitter.com/1.1/favorites/destroy.json'
        self.update_message_url = 'https://api.twitter.com/1.1/statuses/update.json'

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
                    use_proxy=USE_PROXY, **kwargs):
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
    def get_user_timeline(self, token, token_secret, **kwargs):
        if token and token_secret:
            request = self.gen_request('GET', self.user_homeline_url,
                                       resource_owner_key=token,
                                       resource_owner_secret=token_secret,
                                       **kwargs)
            response = yield self.client.fetch(request)
            response = json.loads(response.body.decode())
            if type(response) != list:
                response = []
            statuses = self.extract_raw_statuses(response)
            return statuses

    @staticmethod
    def extract_raw_statuses(data):
        raw_statuses = data
        statuses = []
        for r_s in raw_statuses:
            def extract_r_s(r_s):

                p_s = dict()
                p_s['writer'] = r_s.get('user').get('name')
                p_s['screen_name'] = r_s.get('user').get('screen_name').strip()
                p_s['text'] = re.sub(r'https://t.co/.*', '', r_s.get('text', ''))
                p_s['profile'] = r_s.get('user').get('profile_image_url')
                p_s['time'] = datetime.strptime(r_s.get('created_at'), '%a %b %d %H:%M:%S %z %Y').isoformat()
                p_s['liked'] = r_s.get('favorited')
                p_s['imgs'] = []
                ext_ent = r_s.get('extended_entities')
                if ext_ent:
                    for m in ext_ent.get('media'):
                        if m.get('type', None) == 'photo':
                            p_s['imgs'].append({
                                'middl': m.get('media_url')
                            })
                p_s['type'] = 'twitter'
                p_s['id'] = str(r_s.get('id'))
                quoted_status = r_s.get('quoted_status', None)

                if quoted_status:
                    p_s['retwed_msg'] = extract_r_s(quoted_status)
                    p_s['is_original'] = False
                else:
                    p_s['is_original'] = True

                return p_s

            status = extract_r_s(r_s)
            statuses.append(status)

        return statuses

    @coroutine
    def like_this_msg(self, token, token_secret, msg_id):
        request = self.gen_request('POST', self.like_msg_url, resource_owner_key=token,
                                   resource_owner_secret=token_secret, id=msg_id)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return response.get('favorited')

    @coroutine
    def unlike_this_msg(self, token, token_secret, msg_id):
        request = self.gen_request('POST', self.unlike_msg_url, resource_owner_key=token,
                                   resource_owner_secret=token_secret, id=msg_id)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return response.get('favorited')

    def retw_url(self, msg_id):
        return 'https://api.twitter.com/1.1/statuses/retweet/%s.json' % msg_id

    @coroutine
    def retw_without_comment(self, token, token_secret, msg_id):
        request = self.gen_request('POST', self.retw_url(msg_id), resource_owner_key=token,
                                   resource_owner_secret=token_secret, id=msg_id)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return response.get('retweeted', False)

    @coroutine
    def retw_with_comment(self, token, token_secret, reply_text):
        request = self.gen_request('POST', self.update_message_url, resource_owner_key=token,
                                   resource_owner_secret=token_secret, status=reply_text,
                                   )
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return response.get('created_at', None)

    @coroutine
    def reply_message(self, token, token_secret, msg_id, reply_text):
        request = self.gen_request('POST', self.update_message_url, resource_owner_key=token,
                                   resource_owner_secret=token_secret, status=reply_text,
                                   in_reply_to_status_id=msg_id)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        return response.get('in_reply_to_user_id_str', None)
