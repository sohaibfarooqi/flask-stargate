import os
import unittest
from flask import json, request
import sys
import os
sys.path.insert(0,'..')
from stargate.stargate import Manager
from stargate.stargate.proxy import manager_info
from stargate.stargate.const import ResourceInfoConst
from stargate.app.models import User, City, Location, TestPrimaryKey
from stargate.app import init_app, db
from functools import wraps, partial

"""Test Decorator"""
def auth_key_header(func):
    @wraps(func)
    def new_func(*args, **kw):
        header = request.headers.get('X-AUTH_KEY')
        if header != '1234567':
        	raise ValueError("Invalid AUTH_KEY")
        return func(*args, **kw)
    return new_func

class TestResourceManager(unittest.TestCase):
		
		@classmethod
		def setUpClass(self):
			#Initilize Flask test client
			self.app = init_app(test=True)
			self.client = self.app.test_client()
			#Insert Dummy data for testing
			city = City()
			location = Location()
			user = User()

			manager = Manager(self.app, db)
			manager.register_resource(User, endpoint = 'mycustomcollection', methods = ['GET'])
			manager.register_resource(Location, fields = ['latitude','longitude'])
			manager.register_resource(City, url_prefix = '/v1', exclude = ['latitude','longitude'])
			manager.register_resource(TestPrimaryKey, endpoint = 'testprimarykey', decorators = [auth_key_header], primary_key = 'ser_id')
			
			with self.app.test_request_context():
				db.create_all()
				city.title = "Lahore"
				city.latitude = 72.813
				city.longitude = 78.1987
				db.session.add(city)
				db.session.commit()
				db.session.flush()

				location.title = "Johar Town"
				location.latitude = 72.813
				location.longitude = 78.1987
				location.parent_id = -1
				location.city_id = city.id
			
				db.session.add(location)
				db.session.commit()
				db.session.flush()

				user.name = "John Baptist"
				user.username = "John91"
				user.age = 19
				user.password = "abcdefg"
				user.email = "johnbaptist@gmail.com"
				user.phone = "923349725618"
				user.pic_url = "/images/pic.jpg"
				user.city_id = city.id
				user.location_id = location.id

				db.session.add(user)
				db.session.commit()
				db.session.flush()
		
		
		def test_collection_name(self):
			response = self.client.get('/api/mycustomcollection', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)

			response = self.client.get('/api/mycustomcollection', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)

		def test_url_prefix(self):
			response = self.client.get('/v1/city', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)

		def test_resource_fields(self):
			response = self.client.get('/api/location', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'] )

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
			
				for key in data:
					keys = list(key['attributes'].keys())
					self.assertCountEqual(keys, ['latitude','longitude'])
			else:
				raise ValueError("No-Content")

		def test_resource_exclude(self):
			response = self.client.get('/v1/city', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'] )

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				
				for key in data:
					keys = list(key['attributes'].keys())
					self.assertNotIn(['latitude','longitude'], keys)
			else:
				raise ValueError("No-Content")
		
		
		def test_view_decorators(self):
			response = self.client.get('/api/testprimarykey', headers={"Content-Type": "application/json", "X_AUTH_KEY":"1234567"})
			self.assertEqual(response._status_code, 200)
			
			func = partial(self.client.get, '/api/testprimarykey', headers={"Content-Type": "application/json"})
			self.assertRaises(ValueError, func)
		
		def test_resource_http_methods(self):
			response = self.client.get('/api/mycustomcollection', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)

			response = self.client.post('/api/mycustomcollection', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 405)
		
		def test_custom_primary_key_field(self):
			primary_key = manager_info(ResourceInfoConst.PRIMARY_KEY_FOR, TestPrimaryKey)
			self.assertEqual(primary_key, 'ser_id')
		
		@classmethod
		def tearDownClass(self):
			with self.app.test_request_context():
				db.session.remove()
				db.drop_all()
if __name__ == '__main__':
    unittest.main()