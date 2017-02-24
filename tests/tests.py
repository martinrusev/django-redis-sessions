from redis_sessions.session import SessionStore
from redis_sessions import settings
import time
from nose.tools import eq_, assert_false


##  Dev
import redis
import timeit

redis_session = SessionStore()


def test_modify_and_keys():
    eq_(redis_session.modified, False)
    redis_session['test'] = 'test_me'
    eq_(redis_session.modified, True)
    eq_(redis_session['test'], 'test_me')


def test_session_load_does_not_create_record():
    session = SessionStore('someunknownkey')
    session.load()

    eq_(redis_session.exists(redis_session.session_key), False)


def test_save_and_delete():
    redis_session['key'] = 'value'
    redis_session.save()
    eq_(redis_session.exists(redis_session.session_key), True)
    redis_session.delete(redis_session.session_key)
    eq_(redis_session.exists(redis_session.session_key), False)


def test_flush():
    redis_session['key'] = 'another_value'
    redis_session.save()
    key = redis_session.session_key
    redis_session.flush()
    eq_(redis_session.exists(key), False)


def test_items():
    redis_session['item1'], redis_session['item2'] = 1, 2
    redis_session.save()
    # Python 3.*
    eq_(set(list(redis_session.items())), set([('item2', 2), ('item1', 1)]))


def test_expiry():
    redis_session.set_expiry(1)
    # Test if the expiry age is set correctly
    eq_(redis_session.get_expiry_age(), 1)
    redis_session['key'] = 'expiring_value'
    redis_session.save()
    key = redis_session.session_key
    eq_(redis_session.exists(key), True)
    time.sleep(2)
    eq_(redis_session.exists(key), False)


def test_save_and_load():
    redis_session.set_expiry(60)
    redis_session.setdefault('item_test', 8)
    redis_session.save()
    session_data = redis_session.load()
    eq_(session_data.get('item_test'), 8)

def test_with_redis_url_config():
    settings.SESSION_REDIS_URL = 'redis://localhost'

    from redis_sessions.session import SessionStore

    redis_session = SessionStore()
    server = redis_session.server

    host = server.connection_pool.connection_kwargs.get('host')
    port = server.connection_pool.connection_kwargs.get('port')
    db = server.connection_pool.connection_kwargs.get('db')

    eq_(host, 'localhost')
    eq_(port, 6379)
    eq_(db, 0)

def test_with_unix_url_config():
    pass

    # Uncomment this in `redis.conf`:
    # 
    # unixsocket /tmp/redis.sock
    # unixsocketperm 755

    #settings.SESSION_REDIS_URL = 'unix:///tmp/redis.sock'

    #from redis_sessions.session import SessionStore

    # redis_session = SessionStore()
    # server = redis_session.server
    #
    # host = server.connection_pool.connection_kwargs.get('host')
    # port = server.connection_pool.connection_kwargs.get('port')
    # db = server.connection_pool.connection_kwargs.get('db')
    #
    # eq_(host, 'localhost')
    # eq_(port, 6379)
    # eq_(db, 0)

# def test_load():
#     redis_session.set_expiry(60)
#     redis_session['item1'], redis_session['item2'] = 1,2
#     redis_session.save()
#     session_data = redis_session.server.get(redis_session.session_key)
#     expiry, data = int(session_data[:15]), session_data[15:]
