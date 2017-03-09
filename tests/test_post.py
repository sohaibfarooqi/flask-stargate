from . import TestSetup
from flask import json
import datetime
from app.models import User, City, Location
from app import db

class TestPost(TestSetup):
		
		@classmethod
		def setUpClass(self):
			super(TestPost, self).setUpClass()
		
		def test_simple_post(self):
			request_data = {
					"data": {
						"attributes": {
							"title": "Lahore",
							"latitude": 72.8176,
							"longitude": 79.2998
						}
					}
				}
			response = self.client.post('/api/city', data = json.dumps(request_data), headers={"Content-Type": "application/json"})
			response_doc = json.loads(response.get_data())
			self.assertEqual(response_doc['meta']['status_code'], 201)
			
			data = response_doc['data']
			
			get_response = self.client.get(response.headers.get('rel'), headers={"Content-Type": "application/json"})
			get_response_doc = json.loads(get_response.get_data())
			self.assertDictEqual(get_response_doc['data'], data)
			
		def test_related_instance_post(self):
			request_data_primary = {
					"data": {
						"attributes": {
							"title": "Lahore",
							"latitude": 72.8176,
							"longitude": 79.2998
						}
					}
				}

			response = self.client.post('/api/city', data = json.dumps(request_data_primary), headers={"Content-Type": "application/json"})
			response_doc = json.loads(response.get_data())
			self.assertEqual(response_doc['meta']['status_code'], 201)

			request_data_related = {
					"data": {
						"attributes": {
							"title": "Johar Town",
							"latitude": 72.8176,
							"longitude": 79.2998,
							"parent_id": -1
						},
						"_embedded":{
								"city":{'data':{'id': response_doc['data']['id']}}
						}
					}
				}

			response = self.client.post('/api/location', data = json.dumps(request_data_related), headers={"Content-Type": "application/json"})
			rel_response_doc = json.loads(response.get_data())
			self.assertEqual(rel_response_doc['meta']['status_code'], 201)

			data = rel_response_doc['data']

			get_response = self.client.get("{0}?expand=city".format(response.headers.get('rel')), headers={"Content-Type": "application/json"})
			get_response_doc = json.loads(get_response.get_data())
			self.assertDictEqual(get_response_doc['data'], data)
		
		def test_related_collection_post(self):
			#TODO: Add self links to related resources in serialization.
			#Complete this test case by hitting on self link and comparing data.
			request_data_related = {
					"data": {
						"attributes": {
							"title": "Wapda Town",
							"latitude": 72.8176,
							"longitude": 79.2998,
							"parent_id": -1
						}
					}
				}

			response = self.client.post('/api/location', data = json.dumps(request_data_related), headers={"Content-Type": "application/json"})
			rel_response_doc_1 = json.loads(response.get_data())
			self.assertEqual(rel_response_doc_1['meta']['status_code'], 201)

			request_data_related_second = {
					"data": {
						"attributes": {
							"title": "Faisal Town",
							"latitude": 72.8176,
							"longitude": 79.2998,
							"parent_id": -1
						}
					}
				}

			response = self.client.post('/api/location', data = json.dumps(request_data_related), headers={"Content-Type": "application/json"})
			rel_response_doc_2 = json.loads(response.get_data())
			self.assertEqual(rel_response_doc_2['meta']['status_code'], 201)

			request_data_primary = {
					"data": {
						"attributes": {
							"title": "Lahore",
							"latitude": 72.8176,
							"longitude": 79.2998
						},
						"_embedded":{
							"location":{"data":[{"id":rel_response_doc_1['data']['id']} , {"id":rel_response_doc_2['data']['id']}]}
						}
					}
				}

			response = self.client.post('/api/city', data = json.dumps(request_data_primary), headers={"Content-Type": "application/json"})
			response_doc = json.loads(response.get_data())
			self.assertEqual(response_doc['meta']['status_code'], 201)


		