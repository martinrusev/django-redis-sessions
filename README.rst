django-redis-sessions
=====================

Redis database backend for your sessions

|Build Status|

-  `Installation`_
-  `Available Settings`_
-  `Changelog`_

Installation
============

-  Run ``pip install django-redis-sessions`` or alternatively download
   the tarball and run ``python setup.py install``,

For Django < 1.4 run ``pip install django-redis-sessions==0.3``

-  Set ``redis_sessions.session`` as your session engine, like so:

.. code:: python

    SESSION_ENGINE = 'redis_sessions.session'

Available Settings
==================

.. code:: python

    SESSION_REDIS = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': 'password',
        'prefix': 'session',
        'socket_timeout': 1,
        'retry_on_timeout': False
        }

If you prefer domain socket connection, you can just add this line
instead of HOST and PORT.

.. code:: python

    SESSION_REDIS = {
        'unix_domain_socket_path': '/var/run/redis/redis.sock',
        'db': 0,
        'password': 'password',
        'prefix': 'session',
        'socket_timeout': 1,
        'retry_on_timeout': False
    }

Redis Sentinel
~~~~~~~~~~~~~~

.. code:: python

    SESSION_REDIS_SENTINEL_LIST = [(host, port), (host, port), (host, port)]
    SESSION_REDIS_SENTINEL_MASTER_ALIAS = 'sentinel-master'

Redis Pool (Horizontal partitioning)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Splits sessions between Redis instances based on the session key. You
can configure the connection type for each Redis instance in the pool
(host/port, unix socket, redis url).


.. code:: python

    SESSION_REDIS = {
        'prefix': 'session',
        'socket_timeout': 1
        'retry_on_timeout': False,
        'pool': [{
            'host': 'localhost3',
            'port': 6379,
            'db': 0,
            'password': None,
            'unix_domain_socket_path': None,
            'url': None,
            'weight': 1
        },
        {
            'host': 'localhost2',
            'port': 6379,
            'db': 0,
            'password': None,
            'unix_domain_socket_path': None,
            'url': None,
            'weight': 1
        },
        {
            'host': 'localhost1',
            'port': 6379,
            'db': 0,
            'password': None,
            'unix_domain_socket_path': None,
            'url': None,
            'weight': 1
        }]
    }


Tests
=====

.. code:: bash

    $ pip install -r dev_requirements.txt
    # Make sure you have redis running on localhost:6379
    $ nosetests -v

`Changelog <https://github.com/martinrusev/django-redis-sessions/blob/master/CHANGELOG.md>`__
=============================================================================================

.. _Installation: #installation
.. _Available Settings: #available-settings
.. _Changelog: #changelog

.. |Build Status| image:: https://travis-ci.org/martinrusev/django-redis-sessions.svg?branch=master
   :target: https://travis-ci.org/martinrusev/django-redis-sessions
