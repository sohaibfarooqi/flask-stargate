from . import PaginatedTestBase
from flask import json
import datetime
from app.models import User, City, Location
from app import db
from stargate.const import PaginationConst

class TestPagination(PaginatedTestBase):
		
		@classmethod
		def setUpClass(self):
			super(TestPagination, self).setUpClass()
		
		
		def test_defualt_pagination(self):
			response = self.client.get('/api/user', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			objects = data['data']
			
			link_header = response.headers['rel']
			params = link_header.split('?')[1]
			params = params.split('&')
			
			PAGE_NUMBER= False
			PAGE_SIZE = False
			
			for param in params:
				key, value = param.split('=')
				if key == 'page_number':
					self.assertTrue(int(value) == PaginationConst.PAGE_NUMBER)
					PAGE_NUMBER = True
				
				elif key == 'page_size':
					self.assertTrue(int(value) == PaginationConst.PAGE_SIZE)	
					PAGE_SIZE = True

			self.assertTrue(PAGE_NUMBER == True and PAGE_SIZE == True)
			self.assertTrue(len(objects) == PaginationConst.PAGE_SIZE)

		def test_pagination_params(self):
			response = self.client.get('/api/user?page_number=5&page_size=20', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			objects = data['data']

			link_header = response.headers['rel']
			params = link_header.split('?')[1]
			params = params.split('&')
			
			PAGE_NUMBER= False
			PAGE_SIZE = False
			
			for param in params:
				key, value = param.split('=')
				if key == 'page_number':
					self.assertTrue(int(value) == 5)
					PAGE_NUMBER = True
				
				elif key == 'page_size':
					self.assertTrue(int(value) == 20)	
					PAGE_SIZE = True

			self.assertTrue(PAGE_NUMBER == True and PAGE_SIZE == True)
			self.assertTrue(len(objects) == 20)

		def test_page_size_limit(self):
			response = self.client.get('/api/user?page_number=1&page_size=120', headers={"Content-Type": "application/json"})
			data = json.loads(response.get_data())
			objects = data['data']
			
			link_header = response.headers['rel']
			params = link_header.split('?')[1]
			params = params.split('&')
			
			PAGE_NUMBER= False
			PAGE_SIZE = False
			
			for param in params:
				key, value = param.split('=')
				if key == 'page_number':
					self.assertTrue(int(value) == 1)
					PAGE_NUMBER = True
				
				elif key == 'page_size':
					self.assertTrue(int(value) == PaginationConst.MAX_PAGE_SIZE)	
					PAGE_SIZE = True

			self.assertTrue(PAGE_NUMBER == True and PAGE_SIZE == True)
			self.assertTrue(len(objects) == PaginationConst.MAX_PAGE_SIZE)

		def test_pagination_links(self):
			response = self.client.get('/api/user?page_number=1&page_size=20', headers={"Content-Type": "application/json"})
			
			data = json.loads(response.get_data())
			links = data['links']
			link_keys = ['first', 'last', 'next', 'prev']
			
			self.assertCountEqual(link_keys, links.keys())
				
			link_values = [val for val in links.values() if val is not None]

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
