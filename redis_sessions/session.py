import time
from redis import Redis
from django.utils.encoding import force_unicode
from django.contrib.sessions.backends.base import SessionBase, CreateError

def server():
    return Redis(host="localhost", port=6379, db=0)

class SessionStore(SessionBase):
    """
    Implements Redis database session store.
    """
    def load(self):
        try:
            session_data = server().get(self.session_key)
            expiry, data = int(session_data[:15]), session_data[15:]
            if expiry < time.time():
                return {}
            else:
                return self.decode(force_unicode(data))
        except:
            self.create()
            return {}

    def exists(self, session_key):
        try:
            server()[session_key]
        except:
            return False
        return True

    def create(self):
        while True:
            self.session_key = self._get_new_session_key()
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
        encoded = '%15d%s' % (int(time.time()) + self.get_expiry_age(), data)
        server()[self.session_key] = encoded
    
    def delete(self, session_key=None):
        if session_key is None:
            if self._session_key is None:
                return
            session_key = self._session_key
        try:
            server().delete(session_key)
        except:
            pass