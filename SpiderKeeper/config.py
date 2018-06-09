# Statement for enabling the development environment
import os
import sys

DEBUG = True

# Define the application directory


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath('.'), 'SpiderKeeper.db')
if 'win' in sys.platform:
    SQLALCHEMY_DATABASE_URI = 'mysql://localhost:3306/' + 'SpiderKeeper' + '?user=root&passwd=123456'
    # SQLALCHEMY_DATABASE_URI = 'mysql://218.244.138.88:13456/' + 'Spider01' + '?user=spiderdb&passwd=Cqmyg321'
    # SQLALCHEMY_DATABASE_URI = 'mysql://101.37.174.208:3306/' + 'Spider01' + '?user=root&passwd=32nstmmr2kvuSiMF'
else:
    from requests import get
    ip = get('https://api.ipify.org').text
    if ip == u'101.37.174.208':
        SQLALCHEMY_DATABASE_URI = 'mysql://localhost:3306/' + 'SpiderKeeper' + '?user=root&passwd=123'
    else:
        SQLALCHEMY_DATABASE_URI = 'mysql://192.168.0.1:3307/' + 'SpiderKeeper' + '?user=root&passwd=123456'
        # SQLALCHEMY_DATABASE_URI = 'mysql://218.244.138.88:13456/' + 'SpiderKeeper' + '?user=spiderdb&passwd=Cqmyg321'

SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

# log
LOG_LEVEL = 'INFO'
# LOG_LEVEL = 'ERROR'

# spider services
SERVER_TYPE = 'scrapyd'
# server = ['http://localhost:6800', 'http://121.40.77.248:6800', 'http://101.37.29.42:6800',
#           'http://47.91.166.8:6800', 'http://114.215.177.242:6800']
server = ['http://localhost:6800', 'http://121.40.77.248:6800', 'http://114.215.177.242:6800',
          'http://47.91.166.8:6800']
if "win" in sys.platform:
    SERVERS = server
    # SERVERS = server[1:]

else:
    from requests import get
    ip = get('https://api.ipify.org').text
    if ip == u'101.37.29.42':
        SERVERS = server
    else:
        SERVERS = server[1:]
# basic auth
NO_AUTH = False
BASIC_AUTH_USERNAME = 'admin'
BASIC_AUTH_PASSWORD = 'admin'
BASIC_AUTH_FORCE = True
