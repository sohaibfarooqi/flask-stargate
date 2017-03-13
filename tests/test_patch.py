from . import DescriptiveTestBase
from flask import json
import datetime
from app.models import User, City, Location
from app import db

class TestPatch(DescriptiveTestBase):
		
		@classmethod
		def setUpClass(self):
			super(TestPatch, self).setUpClass()
		
		def test_simple_patch(self):
			test_attr = {"name": "aadddeeefffffff"}
			
			request_data = { "data": { "attributes": test_attr } }
			response = self.client.patch('/api/user/{0}'.format(self.user_list[0].id), data = json.dumps(request_data), headers={"Content-Type": "application/json"})
			response_doc = json.loads(response.get_data())
			self.assertEqual(response_doc['meta']['status_code'], 200)
			
			data = response_doc['data']
			instance_attrs = data['attributes']
			self.assertEqual(instance_attrs.pop('name'), test_attr['name'])
			
			
		