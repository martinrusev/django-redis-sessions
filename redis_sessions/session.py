import redis

try:
    from django.utils.encoding import force_unicode
except ImportError:  # Python 3.*
    from django.utils.encoding import force_text as force_unicode
from django.contrib.sessions.backends.base import SessionBase, CreateError
from redis_sessions import settings


class RedisServer():
    session_key = None
    __redis = {}

    def __init__(self, session_key):
        self.session_key = session_key
        if settings.SESSION_REDIS_SENTINEL_LIST is not None:
            self.connection_type = 'sentinel'
        elif settings.SESSION_REDIS_URL is not None:
            self.connection_type = 'redis_url'
        elif settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH is None:
            self.connection_type = 'unix_url'
        else:
            self.connection_type = 'default'

    def get(self):
        if self.connection_type in self.__redis:
            return self.__redis[self.connection_type]

        if self.connection_type == 'sentinel':
            from redis.sentinel import Sentinel
            self.__redis[self.connection_type] = Sentinel(
                settings.SESSION_REDIS_SENTINEL_LIST,
                socket_timeout=settings.SESSION_REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=settings.SESSION_REDIS_RETRY_ON_TIMEOUT,
                db=getattr(settings, 'SESSION_REDIS_DB', 0),
                password=getattr(settings, 'SESSION_REDIS_PASSWORD', None)
            ).master_for(settings.SESSION_REDIS_SENTINEL_MASTER_ALIAS)

        elif settings.SESSION_REDIS_URL is not None:
            self.__redis[self.connection_type] = redis.StrictRedis.from_url(
                settings.SESSION_REDIS_URL,
                socket_timeout=settings.SESSION_REDIS_SOCKET_TIMEOUT
            )
        elif settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH is None:
            self.__redis[self.connection_type] = redis.StrictRedis(
                host=settings.SESSION_REDIS_HOST,
                port=settings.SESSION_REDIS_PORT,
                socket_timeout=settings.SESSION_REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=settings.SESSION_REDIS_RETRY_ON_TIMEOUT,
                db=settings.SESSION_REDIS_DB,
                password=settings.SESSION_REDIS_PASSWORD
            )
        else:
            self.__redis[self.connection_type] = redis.StrictRedis(
                unix_socket_path=settings.SESSION_REDIS_UNIX_DOMAIN_SOCKET_PATH,
                socket_timeout=settings.SESSION_REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=settings.SESSION_REDIS_RETRY_ON_TIMEOUT,
                db=settings.SESSION_REDIS_DB,
                password=settings.SESSION_REDIS_PASSWORD,
            )

        return self.__redis[self.connection_type]


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
