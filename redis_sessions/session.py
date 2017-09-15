import redis

try:
    from django.utils.encoding import force_unicode
except ImportError:  # Python 3.*
    from django.utils.encoding import force_text as force_unicode
from django.contrib.sessions.backends.base import SessionBase, CreateError
from redis_sessions import settings


class RedisServer():
    __redis = {}

    def __init__(self, session_key):
        self.session_key = session_key
        self.connection_key = ''

        if settings.SESSION_REDIS_SENTINEL_LIST is not None:
            self.connection_type = 'sentinel'
        else:
            if settings.SESSION_REDIS_POOL is not None:
                server_key, server = self.get_server(session_key, settings.SESSION_REDIS_POOL)
                self.connection_key = str(server_key)
                settings.SESSION_REDIS_HOST = getattr(server, 'host', 'localhost')
                settings.SESSION_REDIS_PORT = getattr(server, 'port', 6379)
                settings.SESSION_REDIS_DB = getattr(server, 'db', 0)
                settings.SESSION_REDIS_PASSWORD = getattr(server, 'password', None)
                settings.SESSION_REDIS_URL = getattr(server, 'url', None)
                settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH = getattr(server,'unix_domain_socket_path', None)

            if settings.SESSION_REDIS_URL is not None:
                self.connection_type = 'redis_url'
            elif settings.SESSION_REDIS_HOST is not None:
                self.connection_type = 'redis_host'
            elif settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH is not None:
                self.connection_type = 'redis_unix_url'

        self.connection_key += self.connection_type

    def get_server(self, key, servers_pool):
        total_weight = sum([row.get('weight', 1) for row in servers_pool])
        pos = 0
        for i in range(3, -1, -1):
            pos = pos * 2 ** 8 + ord(key[i])
        pos = pos % total_weight

        pool = iter(servers_pool)
        server = next(pool)
        server_key = 0
        i = 0
        while i < total_weight:
            if i <= pos < (i + server.get('weight', 1)):
                return server_key, server
            i += server.get('weight', 1)
            server = next(pool)
            server_key += 1

        return

    def get(self):
        if self.connection_key in self.__redis:
            return self.__redis[self.connection_key]

        if self.connection_type == 'sentinel':
            from redis.sentinel import Sentinel
            self.__redis[self.connection_key] = Sentinel(
                settings.SESSION_REDIS_SENTINEL_LIST,
                socket_timeout=settings.SESSION_REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=settings.SESSION_REDIS_RETRY_ON_TIMEOUT,
                db=getattr(settings, 'db', 0),
                password=getattr(settings, 'password', None)
            ).master_for(settings.SESSION_REDIS_SENTINEL_MASTER_ALIAS)

        elif self.connection_type == 'redis_url':
            self.__redis[self.connection_key] = redis.StrictRedis.from_url(
                settings.SESSION_REDIS_URL,
                socket_timeout=settings.SESSION_REDIS_SOCKET_TIMEOUT
            )
        elif self.connection_type == 'redis_host':
            self.__redis[self.connection_key] = redis.StrictRedis(
                host=settings.SESSION_REDIS_HOST,
                port=settings.SESSION_REDIS_PORT,
                socket_timeout=settings.SESSION_REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=settings.SESSION_REDIS_RETRY_ON_TIMEOUT,
                db=settings.SESSION_REDIS_DB,
                password=settings.SESSION_REDIS_PASSWORD
            )
        elif self.connection_type == 'redis_unix_url':
            self.__redis[self.connection_key] = redis.StrictRedis(
                unix_socket_path=settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH,
                socket_timeout=settings.SESSION_REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=settings.SESSION_REDIS_RETRY_ON_TIMEOUT,
                db=settings.SESSION_REDIS_DB,
                password=settings.SESSION_REDIS_PASSWORD,
            )

        return self.__redis[self.connection_key]


class SessionStore(SessionBase):
    """
    Implements Redis database session store.
    """
    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)
        self.server = RedisServer(session_key).get()

    def load(self):
        try:
            session_data = self.server.get(
                self.get_real_stored_key(self._get_or_create_session_key())
            )
            return self.decode(force_unicode(session_data))
        except:
            self._session_key = None
            return {}

    def exists(self, session_key):
        return self.server.exists(self.get_real_stored_key(session_key))

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()

            try:
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if self.session_key is None:
            return self.create()
        if must_create and self.exists(self._get_or_create_session_key()):
            raise CreateError
        data = self.encode(self._get_session(no_load=must_create))
        if redis.VERSION[0] >= 2:
            self.server.setex(
                self.get_real_stored_key(self._get_or_create_session_key()),
                self.get_expiry_age(),
                data
            )
        else:
            self.server.set(
                self.get_real_stored_key(self._get_or_create_session_key()),
                data
            )
            self.server.expire(
                self.get_real_stored_key(self._get_or_create_session_key()),
                self.get_expiry_age()
            )

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        try:
            self.server.delete(self.get_real_stored_key(session_key))
        except:
            pass

    def get_real_stored_key(self, session_key):
        """Return the real key name in redis storage
        @return string
        """
        prefix = settings.SESSION_REDIS_PREFIX
        if not prefix:
            return session_key
        return ':'.join([prefix, session_key])
