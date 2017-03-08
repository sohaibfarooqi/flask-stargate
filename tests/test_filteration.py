from . import DescriptiveTestBase
from flask import json
import datetime
from app.models import User, City, Location
from app import db

class TestFilters(DescriptiveTestBase):
		
		@classmethod
		def setUpClass(self):
			super(TestFilters, self).setUpClass()
		
		def test_simple_filter(self):
			filter_list = list() 
			filter_expr = dict(name="name", op="like", val="Vanguard")
			filter_list.append(filter_expr)
			query_str = json.dumps(filter_list)
			response = self.client.get('/api/user?filters={0}'.format(query_str), headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'] )

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				for user in data:
					self.assertEqual(user['attributes']['name'], 'Vanguard')

		def test_conjunction_filter(self):
			filter_list = list() 
			name_list = ["John Doe", "Mark Adams"]
			filter_1 = dict(name="name", op="in", val=','.join(name_list))
			filter_2 = dict(name="age", op="lt", val="25")
			
			combined_filter = list()
			combined_filter.append(filter_1)
			combined_filter.append(filter_2)
			filter_expr = {"or": combined_filter}
			
			filter_list.append(filter_expr)
			query_str = json.dumps(filter_list)
			
			response = self.client.get('/api/user?filters={0}'.format(query_str), headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				for user in data:
					self.assertTrue(any(user['attributes']['name'] == name for name in name_list) or user['attributes']['age'] < 25)

		def test_disjunction_filter(self):
			filter_list = list() 
			
			filter_1 = dict(name="name", op="in", val="Vanguard,Wayne John")
			filter_2 = dict(name="age", op="gt", val="19")
			
			combined_filter = list()
			combined_filter.append(filter_1)
			combined_filter.append(filter_2)
			filter_expr = {"and": combined_filter}
			
			filter_list.append(filter_expr)
			query_str = json.dumps(filter_list)
			
			response = self.client.get('/api/user?filters={0}'.format(query_str), headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'] )

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				for user in data:
					self.assertIn(user['attributes']['name'], ['Vanguard', 'Wayne John'])		
					self.assertGreater(user['attributes']['age'], 19)		