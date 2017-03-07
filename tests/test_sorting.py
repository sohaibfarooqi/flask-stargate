from . import TestSetup
from flask import json
import datetime
from app.models import User, City, Location
from app import db

class TestSorting(TestSetup):
		
		@classmethod
		def setUpClass(self):
			super(TestSorting, self).setUpClass()

		def test_sort_desc(self):
			response = self.client.get('/api/user?sort=-age', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'] )

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				self.assertTrue(all(data[i]['attributes']['age'] >= data[i+1]['attributes']['age'] for i in range(len(data)-1)))

		def test_sort_asc(self):
			response = self.client.get('/api/user?sort=age', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'] )

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				self.assertTrue(all(data[i]['attributes']['age'] <= data[i+1]['attributes']['age'] for i in range(len(data)-1)))		

		def test_sort_multiple(self):
			response = self.client.get('/api/user?sort=age,-created_at', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'] )

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				self.assertTrue(all(data[i]['attributes']['age'] <= data[i+1]['attributes']['age'] and datetime.datetime.strptime(data[i]['attributes']['created_at'], "%Y-%m-%dT%H:%M:%S.%f") >= datetime.datetime.strptime(data[i+1]['attributes']['created_at'], "%Y-%m-%dT%H:%M:%S.%f")for i in range(len(data)-1)))