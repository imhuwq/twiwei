import random
import os

chars = 'abcdefghijklmnopqrstuvwxyz' \
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
        '0123456789~!@#$%^&*(-_+)='

SECRET_COOKIE = ''.join([x for x in random.SystemRandom().choice(chars) for _ in range(60)])

db_config = {
    'username': 'twiwei',
    'password': 'twiwei',
    'database': 'twiwei',
    'host': 'localhost',
    'port': 5432
}
db_uri = 'postgresql+psycopg2://%s:%s@%s:%d/%s' % (db_config.get('username'),
                                                   db_config.get('password'),
                                                   db_config.get('host'),
                                                   db_config.get('port'),
                                                   db_config.get('database'))
settings = {
    "cookie_secret": SECRET_COOKIE,
    "xsrf_cookies": True,
    'login_url': '/login'
}

base_dir = os.path.abspath(os.path.dirname(__file__))

WEI_CLIENT_ID = ''
WEI_CLIENT_SECRET = ''
TWI_CLIENT_ID = ''
TWI_CLIENT_SECRET = ''
WEI_ADMIN_TOKEN = ''
TWI_ADMIN_TOKEN = ''
TWI_ADMIN_TOKEN_SECRET = ''
