from . import SimpleTestBase
from flask import json
import datetime
from app.models import User, City, Location
from app import db

class TestRoutes(SimpleTestBase):
		
		@classmethod
		def setUpClass(self):
			super(TestRoutes, self).setUpClass()
		
		def test_get_collection(self):
			response = self.client.get('/api/user', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)
		
		def test_get_instance(self):
			response = self.client.get('/api/user/1', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)

		def test_get_related_instance(self):
			response = self.client.get('/api/user/1/location/1', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			print(data)
			self.assertEqual(response._status_code, 200)

		def test_get_related_collection(self):
			response = self.client.get('/api/city/1/location', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)