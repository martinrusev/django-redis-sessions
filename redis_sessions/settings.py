from django.conf import settings

# SESSION_REDIS - Default
SESSION_REDIS = getattr(settings, 'SESSION_REDIS', {})

SESSION_REDIS_HOST = SESSION_REDIS.get('host', 'localhost')
SESSION_REDIS_PORT = SESSION_REDIS.get('port', 6379)
SESSION_REDIS_SOCKET_TIMEOUT = SESSION_REDIS.get('socket_timeout', 0.1)
SESSION_REDIS_RETRY_ON_TIMEOUT = SESSION_REDIS.get('retry_on_timeout', False)
SESSION_REDIS_DB = SESSION_REDIS.get('db', 0)
SESSION_REDIS_PREFIX = SESSION_REDIS.get('prefix', '')
SESSION_REDIS_PASSWORD = SESSION_REDIS.get('password', None)
SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH = SESSION_REDIS.get('unix_domain_socket_path', None)
SESSION_REDIS_URL = SESSION_REDIS.get('url', None)


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
SESSION_REDIS_POOL = SESSION_REDIS.get('POOL', None)

# should be on the format [(host, port), (host, port), (host, port)]
SESSION_REDIS_SENTINEL_LIST = getattr(settings, 'SESSION_REDIS_SENTINEL_LIST', None)
SESSION_REDIS_SENTINEL_MASTER_ALIAS = getattr(settings, 'SESSION_REDIS_SENTINEL_MASTER_ALIAS', None)