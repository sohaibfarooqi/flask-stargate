from . import DescriptiveTestBase
from flask import json
import datetime
from app.models import User, City, Location
from app import db

class TestGrouping(DescriptiveTestBase):	
		
		@classmethod
		def setUpClass(self):
			super(TestGrouping, self).setUpClass()
		
		def test_single_group(self):
			response = self.client.get('/api/user?group=age', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			data = data['data']
			age_groups = [user['attributes']['age'] for user in data]
			self.assertTrue(len(age_groups) == len(set(age_groups)))

		def test_multiple_groups(self):
			response = self.client.get('/api/user?group=age,created_at', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			data = data['data']
			age_groups = [user['attributes']['age'] for user in data]
			time_created = [user['attributes']['created_at'] for user in data]
			time_created_set = set(time_created)
			#FIXME: How to test two disctinct grouping? 
			self.assertTrue(len(age_groups) == len(set(age_groups)))

		def test_related_model_grouping(self):
			response = self.client.get('/api/user?group=city.id', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			data = data['data']
			age_groups = [user['attributes']['age'] for user in data]
			self.assertTrue(len(age_groups) == len(set(age_groups)))
