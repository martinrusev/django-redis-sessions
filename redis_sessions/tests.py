from session import SessionStore as RedisSession
import unittest
import time
from nose.tools import eq_

class TestRedisSesssios(unittest.TestCase):

	def setUp(self):
		self.redis_session = RedisSession()

	def test_modify_and_keys(self):
		eq_(self.redis_session.modified, False)
		self.redis_session['test'] = 'test_me'
		
		eq_(self.redis_session.modified, True)
		eq_(self.redis_session['test'], 'test_me')


	def test_save_delete(self):
		self.redis_session['key'] = 'value'
		self.redis_session.save()
		self.redis_session.exists(self.redis_session.session_key)

		self.redis_session.delete(self.redis_session.session_key)
		eq_(self.redis_session.exists(self.redis_session.session_key), False)
		

	def test_flush(self):
		self.redis_session['key'] = 'another_value'
		self.redis_session.save()
		key = self.redis_session.session_key

		self.redis_session.flush()
		eq_(self.redis_session.exists(key), False)

	def test_items(self):
		self.redis_session['item1'], self.redis_session['item2'] = 1,2
		self.redis_session.save()

		eq_(self.redis_session.items(), [('item2', 2), ('item1', 1)])

	def test_expiry(self):
		
		self.redis_session.set_expiry(1) 
		# Test if the expiry age is set correctly
		eq_(self.redis_session.get_expiry_age(), 1)
		
		self.redis_session['key'] = 'expiring_value'
		self.redis_session.save()
		key = self.redis_session.session_key
		
		eq_(self.redis_session.exists(key), True)
		
		time.sleep(2)
		eq_(self.redis_session.exists(key), False)

	#def test_load(self):
		
		#self.redis_session.set_expiry(60)
		#self.redis_session['item1'], self.redis_session['item2'] = 1,2
		#self.redis_session.save()
		
		#session_data =  self.redis_session.server.get(self.redis_session.session_key)
		#expiry, data = int(session_data[:15]), session_data[15:]



if __name__ == '__main__':
	import os
	os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 
	unittest.main()

# To run the test suite
# pip install nose
# python tests.py -v

