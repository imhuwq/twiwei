import requests

from config import WEI_CLIENT_ID, WEI_CLIENT_SECRET, WEI_ADMIN_TOKEN


class Weibo(object):
    def __init__(self):
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

    def access_token(self, code):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': 'twiwei.com/oauth2/weibo/access_token/',
            'code': code
        }
        data = requests.post(self.access_token_url, params).json()
        return data

    def get_user_info(self, token, uid):

        params = {
            'access_token': token,
            'uid': uid
        }
        data = requests.get(self.user_info_url, params).json()
        return {
            'name': data.get('name') + '@weibo',
            'gender': data.get('gender'),
            'avatar': data.get('profile_image_url')
        }

    def get_user_timeline(self, token, **kwargs):
        params = {
            'access_token': token
        }
        for key, value in kwargs.items():
            params[key] = value

        return requests.get(self.user_home_url, params).json()

    def get_pub_timeline(self, token, count=20, page=1):

        params = {
            'access_token': token,
            'count': count,
            'page': page
        }
        return requests.get(self.public_url, params).json()

    @staticmethod
    def extract_raw_status(data):
        raw_statuses = data.get('statuses', [])
        pro_statuses = []
        for r_s in raw_statuses:
            p_s = dict()

            p_s['time'] = r_s.get('created_at')
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
