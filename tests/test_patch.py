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
			
			get_response = self.client.get(response.headers.get('rel'), headers={"Content-Type": "application/json"})

			get_response = json.loads(get_response.get_data())
			data = get_response['data']['attributes']

			self.assertEqual(data.pop('name'), test_attr['name'])

		def test_related_resource_patch(self):
			request_data = { "data": { "_embedded": {"city": {"data":{"id": 2}}} } }
			
			response = self.client.patch('/api/user/{0}'.format(self.user_list[0].id), data = json.dumps(request_data), headers={"Content-Type": "application/json"})
			response_doc = json.loads(response.get_data())
			self.assertEqual(response_doc['meta']['status_code'], 200)

			related_resource = response_doc['data']['_embedded']['city']
			id_tobe_compared = request_data['data']['_embedded']['city']['data']['id']
			self.assertEqual(related_resource['data']['id'], id_tobe_compared)

			self_link = related_resource['data']['_link']

			get_response = self.client.get(self_link, headers={"Content-Type": "application/json"})

			get_response = json.loads(get_response.get_data())
			data = get_response['data']
			self.assertEqual(data.pop('id'), id_tobe_compared)