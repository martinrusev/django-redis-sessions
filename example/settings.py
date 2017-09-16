import os
import sys
current_dir = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)
sys.path.append('/home/martin/personal/django-redis-sessions/redis_sessions')


DEBUG = True
ROOT_URLCONF="app"
DATABASES = {'default': {}}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [current_dir('.')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.template.context_processors.debug',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
            ),
        },
    },
]
SECRET_KEY = 'secret'
MIDDLEWARE = [
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware'
]
INSTALLED_APPS = (
    'django.contrib.sessions',
)
SESSION_ENGINE = 'redis_sessions.session'

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    current_dir('static'),
)


SESSION_REDIS = {
    'host': 'localhost',
    'port': 6378,
    'db': 1,
    'password': 'password',
    'prefix': 'session',
    'socket_timeout': 1
}