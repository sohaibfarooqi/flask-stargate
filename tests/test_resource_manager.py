from . import ManagerTestBase
from flask import json
import datetime
from app import db
from stargate.resource_info import resource_info
from stargate.const import ResourceInfoConst
from app.models import TestPrimaryKey
from app import init_app, db
from functools import partial

class TestResourceManager(ManagerTestBase):
		
		@classmethod
		def setUpClass(self):
			super(TestResourceManager, self).setUpClass()
			
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
			data = json.loads(response.get_data())
			data = data['data']
		
			for key in data:
				keys = list(key['attributes'].keys())
				self.assertCountEqual(keys, ['latitude','longitude'])

		def test_resource_exclude(self):
			response = self.client.get('/v1/city', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			data = data['data']
			
			for key in data:
				keys = list(key['attributes'].keys())
				self.assertNotIn(['latitude','longitude'], keys)
		
		
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
			primary_key = resource_info(ResourceInfoConst.PRIMARY_KEY, TestPrimaryKey)
			self.assertEqual(primary_key, 'ser_id')