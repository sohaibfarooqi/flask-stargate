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

			data = response_doc['data']
			related_resource = data['_embedded']['location']['data']
			
			for resource in related_resource:
				
				resource_url = resource['_link']
				get_response = self.client.get(resource_url, headers={"Content-Type": "application/json"})
				get_response_doc = json.loads(get_response.get_data())
				resource.pop('_link')
				response_obj = get_response_doc['data']
				response_obj.pop('_embedded')
				response_obj.pop('_link')

				self.assertDictEqual(response_obj, resource)
				
			get_response = self.client.get(response.headers.get('rel'), headers={"Content-Type": "application/json"})
			get_response_doc = json.loads(get_response.get_data())
			response_obj = get_response_doc['data']
			
			response_obj.pop('_embedded')
			response_obj.pop('_link')

			data.pop('_embedded')
			data.pop('_link')

			self.assertDictEqual(response_obj, data)

		def test_related_resource_creation(self):
			request_data = {
							"data": {
								"attributes": {
									"title": "Iqbal Town",
									"latitude": 72.8176,
									"longitude": 79.2998,
									"parent_id": -1
									},
								"_embedded":{
									"city":{'data':{"title": "Multan", "latitude": 72.997, "longitude": 78.1234}}
								}
							}
						}

			response = self.client.post('/api/location', data = json.dumps(request_data), headers={"Content-Type": "application/json"})
			response_doc = json.loads(response.get_data())
			self.assertEqual(response_doc['meta']['status_code'], 201)
			related = response_doc['data']['_embedded']['city']['data']

			resource_url = related.pop('_link')

			get_response = self.client.get(resource_url, headers={"Content-Type": "application/json"})
			get_response_doc = json.loads(get_response.get_data())
			response_obj = get_response_doc['data']
			
			response_obj.pop('_embedded')
			response_obj.pop('_link')

			self.assertDictEqual(related, response_obj)			