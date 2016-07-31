import random
import os

DB_CONFIG = {
    'username': 'twiwei',
    'password': 'twiwei',
    'database': 'twiwei',
    'host': 'localhost',
    'port': 5432
}

USE_PROXY = True

WEI_CLIENT_ID = ''
WEI_CLIENT_SECRET = ''
TWI_CLIENT_ID = ''
TWI_CLIENT_SECRET = ''
WEI_ADMIN_TOKEN = ''
TWI_ADMIN_TOKEN = ''
TWI_ADMIN_TOKEN_SECRET = ''


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

CHARS = 'abcdefghijklmnopqrstuvwxyz' \
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
        '0123456789~!@#$%^&*(-_+)='

SECRET_COOKIE = ''.join([x for x in random.SystemRandom().choice(CHARS) for _ in range(60)])

settings = {
    "cookie_secret": SECRET_COOKIE,
    "xsrf_cookies": True,
    'login_url': '/login',
    'template_path': BASE_DIR + '/app/templates/',
    'static_path': BASE_DIR + '/app/static'
}

DB_URI = 'postgresql+psycopg2://%s:%s@%s:%d/%s' % (DB_CONFIG.get('username'),
                                                   DB_CONFIG.get('password'),
                                                   DB_CONFIG.get('host'),
                                                   DB_CONFIG.get('port'),
                                                   DB_CONFIG.get('database'))
