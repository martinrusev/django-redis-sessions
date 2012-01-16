django-redis-sessions
=======================
Redis database backend for your sessions


------------
Installation
------------

1. Run ``pip install django-redis-sessions`` or alternatively  download the tarball and run ``python setup.py install``,

2. Set ``redis_sessions.session`` as your session engine, like so::

       SESSION_ENGINE = 'redis_sessions.session'
		
3. Optional settings::

       SESSION_REDIS_HOST = 'localhost'
       SESSION_REDIS_PORT = 6379
       SESSION_REDIS_DB = 0
       SESSION_REDIS_PASSWORD = 'password'
		
4. That's it
	   
