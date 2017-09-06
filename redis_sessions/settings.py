from django.conf import settings

# SESSION_REDIS - Default
SESSION_REDIS = getattr(settings, 'SESSION_REDIS', {})


SESSION_REDIS_HOST = getattr(SESSION_REDIS, 'HOST', 'localhost')
SESSION_REDIS_PORT = getattr(SESSION_REDIS, 'PORT', 6379)
SESSION_REDIS_SOCKET_TIMEOUT = getattr(SESSION_REDIS, 'SOCKET_TIMEOUT', 0.1)
SESSION_REDIS_RETRY_ON_TIMEOUT = getattr(SESSION_REDIS, 'RETRY_ON_TIMEOUT', False)
SESSION_REDIS_DB = getattr(SESSION_REDIS, 'DB', 0)
SESSION_REDIS_PREFIX = getattr(SESSION_REDIS, 'PREFIX', '')
SESSION_REDIS_PASSWORD = getattr(SESSION_REDIS, 'PASSWORD', None)
SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH = getattr(SESSION_REDIS, 'UNIX_DOMAIN_SOCKET_PATH', None)
SESSION_REDIS_URL = getattr(SESSION_REDIS, 'URL', None)

"""
Should be on the format:
[
    {
        'HOST': 'localhost2',
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': None,
        'UNIX_DOMAIN_SOCKET_PATH': None,
        'URL': None,
        'WEIGHT': 1,
    },
    {
        'HOST': 'localhost1',
        'PORT': 6379,
        'DB': 0,
        'PASSWORD': None,
        'UNIX_DOMAIN_SOCKET_PATH': None,
        'URL': None,
        'WEIGHT': 1,
    },
]
"""
SESSION_REDIS_POOL = getattr(SESSION_REDIS, 'POOL', None)

# should be on the format [(host, port), (host, port), (host, port)]
SESSION_REDIS_SENTINEL_LIST = getattr(settings, 'SESSION_REDIS_SENTINEL_LIST', None)
SESSION_REDIS_SENTINEL_MASTER_ALIAS = getattr(settings, 'SESSION_REDIS_SENTINEL_MASTER_ALIAS', None)