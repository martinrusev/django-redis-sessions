from django.conf import settings

# SESSION_REDIS - Default
SESSION_REDIS = getattr(settings, 'SESSION_REDIS', {})


SESSION_REDIS_HOST = getattr(SESSION_REDIS, 'host', 'localhost')
SESSION_REDIS_PORT = getattr(SESSION_REDIS, 'port', 6379)
SESSION_REDIS_SOCKET_TIMEOUT = getattr(SESSION_REDIS, 'socket_timeout', 0.1)
SESSION_REDIS_RETRY_ON_TIMEOUT = getattr(SESSION_REDIS, 'retry_on_timeout', False)
SESSION_REDIS_DB = getattr(SESSION_REDIS, 'db', 0)
SESSION_REDIS_PREFIX = getattr(SESSION_REDIS, 'prefix', '')
SESSION_REDIS_PASSWORD = getattr(SESSION_REDIS, 'password', None)
SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH = getattr(SESSION_REDIS, 'unix_domain_socket_path', None)
SESSION_REDIS_URL = getattr(SESSION_REDIS, 'url', None)

"""
Should be on the format:
[
    {
        'host': 'localhost2',
        'port': 6379,
        'db': 0,
        'password': None,
        'unix_domain_socket_path': None,
        'url': None,
        'weight': 1,
    },
    {
        'host': 'localhost1',
        'port': 6379,
        'db': 0,
        'password': None,
        'unix_domain_socket_path': None,
        'url': None,
        'weight': 1,
    },
]
"""
SESSION_REDIS_POOL = getattr(SESSION_REDIS, 'POOL', None)

# should be on the format [(host, port), (host, port), (host, port)]
SESSION_REDIS_SENTINEL_LIST = getattr(settings, 'SESSION_REDIS_SENTINEL_LIST', None)
SESSION_REDIS_SENTINEL_MASTER_ALIAS = getattr(settings, 'SESSION_REDIS_SENTINEL_MASTER_ALIAS', None)