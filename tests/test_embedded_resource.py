from . import PaginatedTestBase
from flask import json
import datetime
from app import db
from stargate.const import RelTypeConst

class TestEmbeddedResources(PaginatedTestBase):
		
		@classmethod
		def setUpClass(self):
			super(TestEmbeddedResources, self).setUpClass()

		def test_to_many_type(self):
			response = self.client.get('/api/city/1', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			relation_type = data['data']['_embedded']['user']['meta']['_type']
			self.assertEqual(relation_type, RelTypeConst.TO_MANY)

		def test_to_one_type(self):
			response = self.client.get('/api/user/1', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			relation_type = data['data']['_embedded']['city']['meta']['_type']
			self.assertEqual(relation_type, RelTypeConst.TO_ONE)

		def test_embedded_self_link(self):
			#TO_ONE
			response = self.client.get('/api/user/1', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			self_rel = data['data']['_embedded']['city']['meta']['_links']['self']
			self.assertEqual(self_rel, 'http://localhost:5000/api/user/1/city/1')

			#TO_MANY
			response = self.client.get('/api/city/1', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			self_rel = data['data']['_embedded']['user']['meta']['_links']['self']
			
			#LAZY
			self.assertEqual(self_rel, 'http://localhost:5000/api/city/1/user?page_number=1&page_size=10')
			
			#EAGER
			self_rel = data['data']['_embedded']['location']['meta']['_links']['self']
			self.assertEqual(self_rel, 'http://localhost:5000/api/city/1/location')
				
		def test_embedded_pagination_links(self):
			response = self.client.get('/api/city/1?expand=user', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			pagination_links = data['data']['_embedded']['user']['meta']['_links']
			pagination_link_keys = [link for link in pagination_links.keys() if link != 'self']
			
			link_keys = ['first', 'last', 'next', 'prev']
			
			self.assertCountEqual(link_keys, pagination_link_keys)
			link_values = [val for val in pagination_links.values() if val is not None]

			for link in link_values:
				params = link.split('?')[1]
				params = params.split('&')
				
				PAGE_NUMBER = 0
				PAGE_SIZE = 0
				
				for param in params:
					key, value = param.split('=')
					if key == 'page_number':
						PAGE_NUMBER = int(value)
				
					elif key == 'page_size':
						PAGE_SIZE = int(value)

				pag_response = self.client.get(link, headers={"Content-Type": "application/json"})
				link_header = pag_response.headers['rel']
				link_params = link_header.split('?')[1]
				link_params = link_params.split('&')
				
				page_number= 0
				page_size = 0
			
				for link_param in link_params:
					key, value = link_param.split('=')
					if key == 'page_number':
						page_number = int(value)
				
					elif key == 'page_size':	
						page_size = int(value)

				self.assertTrue(PAGE_NUMBER == page_number and PAGE_SIZE == page_size)
				