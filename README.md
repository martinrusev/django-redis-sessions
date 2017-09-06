django-redis-sessions
=======================
Redis database backend for your sessions


[![Build Status](https://travis-ci.org/martinrusev/django-redis-sessions.svg?branch=master)](https://travis-ci.org/martinrusev/django-redis-sessions)


Installation
============

* Run `pip install django-redis-sessions` or alternatively  download the tarball and run `python setup.py install`,

For Django < 1.4 run `pip install django-redis-sessions==0.3`

* Set `redis_sessions.session` as your session engine, like so:


```
SESSION_ENGINE = 'redis_sessions.session'
```

* Optional settings:

```
SESSION_REDIS = {
    'HOST': 'localhost'
    'PORT': 6379
    'REDIS_DB': 0,
    'PASSWORD': 'password',
    'PREFIX': 'session',
    'SOCKET_TIMEOUT': 1
}
# If you prefer domain socket connection, 
# you can just add this line instead of HOST and PORT.

```
SESSION_REDIS = {
    'UNIX_DOMAIN_SOCKET_PATH': '/var/run/redis/redis.sock',
    'REDIS_DB': 0,
    'PASSWORD': 'password',
    'PREFIX': 'session',
    'SOCKET_TIMEOUT': 1
}
```



# Redis Sentinel 
SESSION_REDIS_SENTINEL_LIST = [(host, port), (host, port), (host, port)]
SESSION_REDIS_SENTINEL_MASTER_ALIAS = 'sentinel-master'

# Redis Pool (Horizontal partitioning)
# Splits sessions between Redis instances based on the session key.
# You can configure the connection type for each Redis instance in the pool (host/port, unix socket, redis url). 

```
SESSION_REDIS = {
    'PREFIX': 'session',
    'SOCKET_TIMEOUT': 1
    'RETRY_ON_TIMEOUT': False,
    'POOL': [
        {
            'HOST': 'localhost3',
            'PORT': 6379,
            'DB': 0,
            'PASSWORD': None,
            'UNIX_DOMAIN_SOCKET_PATH': None,
            'URL': None,
            'WEIGHT': 1
        },
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
    }
    ]
}
```



Tests
============


```
$ pip install -r dev_requirements.txt
# Make sure you have redis running on localhost:6379
$ nosetests 
```

# [Changelog](https://github.com/martinrusev/django-redis-sessions/blob/master/CHANGELOG.md)
