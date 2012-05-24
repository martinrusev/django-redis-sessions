import redis
from django.utils.encoding import force_unicode
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.conf import settings


class SessionStore(SessionBase):
    """
    Implements Redis database session store.
    """
    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)
        self.server = redis.StrictRedis(
            host=getattr(settings, 'SESSION_REDIS_HOST', 'localhost'),
            port=getattr(settings, 'SESSION_REDIS_PORT', 6379),
            db=getattr(settings, 'SESSION_REDIS_DB', 0),
            password=getattr(settings, 'SESSION_REDIS_PASSWORD', None)
        )

    def load(self):
        try:
            session_data = self.server.get(self.get_real_stored_key(self.session_key))
            return self.decode(force_unicode(session_data))
        except:
            self.create()
            return {}

    def exists(self, session_key):
        return self.server.exists(self.get_real_stored_key(session_key))

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if must_create and self.exists(self.session_key):
            raise CreateError
        data = self.encode(self._get_session(no_load=must_create))
        self.server.set(self.get_real_stored_key(self.session_key), data)
        self.server.expire(self.get_real_stored_key(self.session_key), self.get_expiry_age())

    def delete(self, session_key=None):
        if session_key is None:
            if self._session_key is None:
                return
            session_key = self._session_key
        try:
            self.server.delete(self.get_real_stored_key(session_key))
        except:
            pass

    def get_real_stored_key(self, session_key):
        """Return the real key name in redis storage
        @return string
        """
        prefix = getattr(settings, 'SESSION_REDIS_PREFIX', '')
        if not prefix:
            return session_key
        return ':'.join([prefix, session_key])
