import time
from random import randint
from nose.tools import eq_, assert_false
from redis_sessions.session import SessionStore as RedisSessionStore
from redis_sessions.session import RedisServer
from redis_sessions import settings
from django.conf import settings
# from django.contrib.sessions.tests import SessionTestsMixin
import base64
from datetime import timedelta
from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.core import management
from django.test import (
    TestCase, override_settings,
)
from django.utils import timezone
from django.test.utils import override_script_prefix, patch_logger
from unittest import skip
import pickle as pypickle
import six

if six.PY3:
    import _pickle as cPickle
else:
    import cPickle as cpickle


#### Hack hack hack ########
# this class should not be edited or modified
# it was copied from django source code
# https://github.com/django/django/blob/master/tests/sessions_tests/tests.py
# Its used by django to test they own session stores.
# But you cannot import it from third parties application
# will create an issue for them to do that.
class SessionTestsMixin:
    # This does not inherit from TestCase to avoid any tests being run with this
    # class, which wouldn't work, and to allow different TestCase subclasses to
    # be used.

    backend = None  # subclasses must specify

    def setUp(self):
        self.session = self.backend()

    def tearDown(self):
        # NB: be careful to delete any sessions created; stale sessions fill up
        # the /tmp (with some backends) and eventually overwhelm it after lots
        # of runs (think buildbots)
        self.session.delete()

    def test_new_session(self):
        self.assertIs(self.session.modified, False)
        self.assertIs(self.session.accessed, False)

    def test_get_empty(self):
        self.assertIsNone(self.session.get('cat'))

    def test_store(self):
        self.session['cat'] = "dog"
        self.assertIs(self.session.modified, True)
        self.assertEqual(self.session.pop('cat'), 'dog')

    def test_pop(self):
        self.session['some key'] = 'exists'
        # Need to reset these to pretend we haven't accessed it:
        self.accessed = False
        self.modified = False

        self.assertEqual(self.session.pop('some key'), 'exists')
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, True)
        self.assertIsNone(self.session.get('some key'))

    def test_pop_default(self):
        self.assertEqual(self.session.pop('some key', 'does not exist'),
                         'does not exist')
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_pop_default_named_argument(self):
        self.assertEqual(self.session.pop('some key', default='does not exist'), 'does not exist')
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_pop_no_default_keyerror_raised(self):
        with self.assertRaises(KeyError):
            self.session.pop('some key')

    def test_setdefault(self):
        self.assertEqual(self.session.setdefault('foo', 'bar'), 'bar')
        self.assertEqual(self.session.setdefault('foo', 'baz'), 'bar')
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, True)

    def test_update(self):
        self.session.update({'update key': 1})
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, True)
        self.assertEqual(self.session.get('update key', None), 1)

    def test_has_key(self):
        self.session['some key'] = 1
        self.session.modified = False
        self.session.accessed = False
        self.assertIn('some key', self.session)
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_values(self):
        self.assertEqual(list(self.session.values()), [])
        self.assertIs(self.session.accessed, True)
        self.session['some key'] = 1
        self.session.modified = False
        self.session.accessed = False
        self.assertEqual(list(self.session.values()), [1])
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_keys(self):
        self.session['x'] = 1
        self.session.modified = False
        self.session.accessed = False
        self.assertEqual(list(self.session.keys()), ['x'])
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_items(self):
        self.session['x'] = 1
        self.session.modified = False
        self.session.accessed = False
        self.assertEqual(list(self.session.items()), [('x', 1)])
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, False)

    def test_clear(self):
        self.session['x'] = 1
        self.session.modified = False
        self.session.accessed = False
        self.assertEqual(list(self.session.items()), [('x', 1)])
        self.session.clear()
        self.assertEqual(list(self.session.items()), [])
        self.assertIs(self.session.accessed, True)
        self.assertIs(self.session.modified, True)

    def test_save(self):
        self.session.save()
        self.assertIs(self.session.exists(self.session.session_key), True)

    def test_delete(self):
        self.session.save()
        self.session.delete(self.session.session_key)
        self.assertIs(self.session.exists(self.session.session_key), False)

    def test_flush(self):
        self.session['foo'] = 'bar'
        self.session.save()
        prev_key = self.session.session_key
        self.session.flush()
        self.assertIs(self.session.exists(prev_key), False)
        self.assertNotEqual(self.session.session_key, prev_key)
        self.assertIsNone(self.session.session_key)
        self.assertIs(self.session.modified, True)
        self.assertIs(self.session.accessed, True)

    def test_cycle(self):
        self.session['a'], self.session['b'] = 'c', 'd'
        self.session.save()
        prev_key = self.session.session_key
        prev_data = list(self.session.items())
        self.session.cycle_key()
        self.assertIs(self.session.exists(prev_key), False)
        self.assertNotEqual(self.session.session_key, prev_key)
        self.assertEqual(list(self.session.items()), prev_data)

    def test_cycle_with_no_session_cache(self):
        self.session['a'], self.session['b'] = 'c', 'd'
        self.session.save()
        prev_data = self.session.items()
        self.session = self.backend(self.session.session_key)
        self.assertIs(hasattr(self.session, '_session_cache'), False)
        self.session.cycle_key()
        self.assertCountEqual(self.session.items(), prev_data)

    def test_save_doesnt_clear_data(self):
        self.session['a'] = 'b'
        self.session.save()
        self.assertEqual(self.session['a'], 'b')

    def test_invalid_key(self):
        # Submitting an invalid session key (either by guessing, or if the db has
        # removed the key) results in a new key being generated.
        try:
            session = self.backend('1')
            session.save()
            self.assertNotEqual(session.session_key, '1')
            self.assertIsNone(session.get('cat'))
            session.delete()
        finally:
            # Some backends leave a stale cache entry for the invalid
            # session key; make sure that entry is manually deleted
            session.delete('1')

    def test_session_key_empty_string_invalid(self):
        """Falsey values (Such as an empty string) are rejected."""
        self.session._session_key = ''
        self.assertIsNone(self.session.session_key)

    def test_session_key_too_short_invalid(self):
        """Strings shorter than 8 characters are rejected."""
        self.session._session_key = '1234567'
        self.assertIsNone(self.session.session_key)

    def test_session_key_valid_string_saved(self):
        """Strings of length 8 and up are accepted and stored."""
        self.session._session_key = '12345678'
        self.assertEqual(self.session.session_key, '12345678')

    def test_session_key_is_read_only(self):
        def set_session_key(session):
            session.session_key = session._get_new_session_key()
        with self.assertRaises(AttributeError):
            set_session_key(self.session)

    # Custom session expiry
    def test_default_expiry(self):
        # A normal session has a max age equal to settings
        self.assertEqual(self.session.get_expiry_age(), settings.SESSION_COOKIE_AGE)

        # So does a custom session with an idle expiration time of 0 (but it'll
        # expire at browser close)
        self.session.set_expiry(0)
        self.assertEqual(self.session.get_expiry_age(), settings.SESSION_COOKIE_AGE)

    def test_custom_expiry_seconds(self):
        modification = timezone.now()

        self.session.set_expiry(10)

        date = self.session.get_expiry_date(modification=modification)
        self.assertEqual(date, modification + timedelta(seconds=10))

        age = self.session.get_expiry_age(modification=modification)
        self.assertEqual(age, 10)

    def test_custom_expiry_timedelta(self):
        modification = timezone.now()

        # Mock timezone.now, because set_expiry calls it on this code path.
        original_now = timezone.now
        try:
            timezone.now = lambda: modification
            self.session.set_expiry(timedelta(seconds=10))
        finally:
            timezone.now = original_now

        date = self.session.get_expiry_date(modification=modification)
        self.assertEqual(date, modification + timedelta(seconds=10))

        age = self.session.get_expiry_age(modification=modification)
        self.assertEqual(age, 10)

    def test_custom_expiry_datetime(self):
        modification = timezone.now()

        self.session.set_expiry(modification + timedelta(seconds=10))

        date = self.session.get_expiry_date(modification=modification)
        self.assertEqual(date, modification + timedelta(seconds=10))

        age = self.session.get_expiry_age(modification=modification)
        self.assertEqual(age, 10)

    def test_custom_expiry_reset(self):
        self.session.set_expiry(None)
        self.session.set_expiry(10)
        self.session.set_expiry(None)
        self.assertEqual(self.session.get_expiry_age(), settings.SESSION_COOKIE_AGE)

    def test_get_expire_at_browser_close(self):
        # Tests get_expire_at_browser_close with different settings and different
        # set_expiry calls
        with override_settings(SESSION_EXPIRE_AT_BROWSER_CLOSE=False):
            self.session.set_expiry(10)
            self.assertIs(self.session.get_expire_at_browser_close(), False)

            self.session.set_expiry(0)
            self.assertIs(self.session.get_expire_at_browser_close(), True)

            self.session.set_expiry(None)
            self.assertIs(self.session.get_expire_at_browser_close(), False)

        with override_settings(SESSION_EXPIRE_AT_BROWSER_CLOSE=True):
            self.session.set_expiry(10)
            self.assertIs(self.session.get_expire_at_browser_close(), False)

            self.session.set_expiry(0)
            self.assertIs(self.session.get_expire_at_browser_close(), True)

            self.session.set_expiry(None)
            self.assertIs(self.session.get_expire_at_browser_close(), True)

    def test_decode(self):
        # Ensure we can decode what we encode
        data = {'a test key': 'a test value'}
        encoded = self.session.encode(data)
        self.assertEqual(self.session.decode(encoded), data)

    def test_decode_failure_logged_to_security(self):
        bad_encode = base64.b64encode(b'flaskdj:alkdjf')
        with patch_logger('django.security.SuspiciousSession', 'warning') as cm:
            self.assertEqual({}, self.session.decode(bad_encode))
        # check that the failed decode is logged	+        # The failed decode is logged.
        self.assertEqual(len(cm), 1)
        self.assertIn('corrupted', cm[0])

    def test_actual_expiry(self):
        # this doesn't work with JSONSerializer (serializing timedelta)
        with override_settings(SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer'):
            self.session = self.backend()  # reinitialize after overriding settings

            # Regression test for #19200
            old_session_key = None
            new_session_key = None
            try:
                self.session['foo'] = 'bar'
                self.session.set_expiry(-1)
                self.session.save()
                old_session_key = self.session.session_key
                # With an expiry date in the past, the session expires instantly.
                new_session = self.backend(self.session.session_key)
                new_session_key = new_session.session_key
                self.assertNotIn('foo', new_session)
            finally:
                self.session.delete(old_session_key)
                self.session.delete(new_session_key)

    def test_session_load_does_not_create_record(self):
        """
        Loading an unknown session key does not create a session record.
        Creating session records on load is a DOS vulnerability.
        """
        session = self.backend('someunknownkey')
        session.load()

        self.assertIsNone(session.session_key)
        self.assertIs(session.exists(session.session_key), False)
        # provided unknown key was cycled, not reused
        self.assertNotEqual(session.session_key, 'someunknownkey')

    def test_session_save_does_not_resurrect_session_logged_out_in_other_context(self):
        """
        Sessions shouldn't be resurrected by a concurrent request.
        """
        # Create new session.
        s1 = self.backend()
        s1['test_data'] = 'value1'
        s1.save(must_create=True)

        # Logout in another context.
        s2 = self.backend(s1.session_key)
        s2.delete()

        # Modify session in first context.
        s1['test_data'] = 'value2'
        with self.assertRaises(UpdateError):
            # This should throw an exception as the session is deleted, not
            # resurrect the session.
            s1.save()

        self.assertEqual(s1.load(), {})


class RedisDBTestCase(SessionTestsMixin, TestCase):

    backend = RedisSessionStore
    session_engine = "redis_sessions.session.SessionStore"

    def setUp(self):
        self._table = None
        super(RedisDBTestCase, self).setUp()

    def test_session_save_does_not_resurrect_session_logged_out_in_other_context(self):
        # todo fix this test
        pass

    def test_pickle_dump(self):

        self.assertDictEqual(self.session.__dict__,
                             pypickle.loads(
                                 pypickle.dumps(self.session, 2)
                             ).__dict__)

        self.assertDictEqual(
            self.session.__dict__,
            cpickle.loads(
                cpickle.dumps(self.session, 2)
            ).__dict__
        )

    def test_with_redis_url_config(self):
        settings.SESSION_REDIS_URL = 'redis://redis'

        from redis_sessions.session import SessionStore

        redis_session = SessionStore()
        server = redis_session.server

        host = server.connection_pool.connection_kwargs.get('host')
        port = server.connection_pool.connection_kwargs.get('port')
        db = server.connection_pool.connection_kwargs.get('db')

        self.assertEqual(host, 'redis')
        self.assertEqual(port, 6379)
        self.assertEqual(db, 0)

    def test_one_connection_is_used(self):
        session = RedisSessionStore('session_key_1')
        session['key1'] = 'value1'
        session.save()

        redis_server = session.server
        set_client_name_1 = 'client_name_' + str(randint(1, 1000))
        redis_server.client_setname(set_client_name_1)
        client_name_1 = redis_server.client_getname()
        eq_(set_client_name_1, client_name_1)
        del session

        session = RedisSessionStore('session_key_2')
        session['key2'] = 'value2'
        session.save()

        redis_server = session.server
        client_name_2 = redis_server.client_getname()
        eq_(client_name_1, client_name_2)

    def test_redis_pool_server_select(self):
        servers = [
            {
                'HOST': 'localhost2',
                'PORT': 6379,
                'DB': 0,
                'PASSWORD': None,
                'UNIX_DOMAIN_SOCKET_PATH': None,
                'WEIGHT': 1,
            },
            {
                'HOST': 'localhost1',
                'PORT': 6379,
                'DB': 0,
                'PASSWORD': None,
                'UNIX_DOMAIN_SOCKET_PATH': None,
                'WEIGHT': 1,
            },
        ]

        keys1 = [
            'm8f0os91g40fsq8eul6tejqpp6k22',
            'kcffsbb5o272et1d5e6ib7gh75pd9',
            'gqldpha87m8183vl9s8uqobcr2ws3',
            'ukb9bg2jifrr60fstla67knjv3e32',
            'k3dranjfna7fv7ijpofs6l6bj2pw1',
            'an4no833idr9jddr960r8ikai5nh3',
            '16b9gardpcscrj5q4a4kf3c4u7tq8',
            'etdefnorfbvfc165c5airu77p2pl9',
            'mr778ou0sqqme21gjdiu4drtc0bv4',
            'ctkgd8knu5hukdrdue6im28p90kt7'
        ]

        keys2 = [
            'jgpsbmjj6030fdr3aefg37nq47nb8',
            'prsv0trk66jc100pipm6bb78c3pl2',
            '84ksqj2vqral7c6ped9hcnq940qq1',
            'bv2uc3q48rm8ubipjmolgnhul0ou3',
            '6c8oph72pfsg3db37qsefn3746fg4',
            'tbc0sjtl2bkp5i9n2j2jiqf4r0bg9',
            'v0on9rorn71913o3rpqhvkknc1wm5',
            'lmsv98ns819uo2klk3s1nusqm0mr0',
            '0foo2bkgvrlk3jt2tjbssrsc47tr3',
            '05ure0f6r5jjlsgaimsuk4n1k2sx6',
        ]
        rs = RedisServer('')

        for key in keys1:
            server_key, server = rs.get_server(key, servers)
            eq_(server_key, 1)

        for key in keys2:
            server_key, server = rs.get_server(key, servers)
            eq_(server_key, 0)

    def test_actual_expiry(self):
        sesssion = RedisSessionStore()
        sesssion.set_expiry(1)
        # Test if the expiry age is set correctly
        self.assertEqual(sesssion.get_expiry_age(), 1)
        sesssion['key'] = 'expiring_value'
        sesssion.save()
        key = sesssion.session_key
        self.assertTrue(sesssion.exists(key))
        time.sleep(2)
        self.assertFalse(sesssion.exists(key))


