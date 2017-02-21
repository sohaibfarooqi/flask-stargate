import os
import datetime
import unittest
from flask import Flask, json
import sys
import os
sys.path.insert(0,'..')
from stargate.stargate import ResourceManager
from stargate.stargate.views.resource import STARGATE_DEFAULT_PAGE_SIZE, STARGATE_DEFAULT_PAGE_NUMBER, STARGATE_DEFAULT_MAX_PAGE_SIZE
from stargate.app.models import User, City, Location
from stargate.app import init_app, db

class TestSorting(unittest.TestCase):
		
		@classmethod
		def setUpClass(self):
			#Initilize Flask test client
			self.app = init_app(test=True)
			self.client = self.app.test_client()
			#Register Models with manager instance
			self.manager = ResourceManager(self.app, db)
			self.manager.register_resource(User, methods = ['GET'])
			self.manager.register_resource(Location, methods = ['GET'])
			self.manager.register_resource(City, methods = ['GET'])
			#Insert Dummy data for testing
			city = City()
			location = Location()

			with self.app.test_request_context():
				db.create_all()
				city.title = "Lahore"
				city.latitude = 72.813
				city.longitude = 78.1987
				db.session.add(city)
				db.session.commit()
				db.session.flush()

				location.title = "Johar Town"
				location.latitude = 72.813
				location.longitude = 78.1987
				location.parent_id = -1
				location.city_id = city.id
			
				db.session.add(location)
				db.session.commit()
				db.session.flush()
				
				user_list = list()
				for i in range(0,120):
					user = User(name = "John Doe", 
								age = 19, 
								username = "John91", 
								password = 'abcdef', 
								email = "johnbaptist@gmail.com", 
								phone = "923349725618",
								pic_url = "/images/john.jpg", 
								city_id = city.id, 
								location_id = location.id)

					user_list.append(user)
				
				db.session.bulk_save_objects(user_list)
				db.session.commit()
				db.session.flush()
		
		
		def test_defualt_pagination(self):
			response = self.client.get('/api/user', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
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
						self.assertTrue(int(value) == STARGATE_DEFAULT_PAGE_NUMBER)
						PAGE_NUMBER = True
					
					elif key == 'page_size':
						self.assertTrue(int(value) == STARGATE_DEFAULT_PAGE_SIZE)	
						PAGE_SIZE = True

				self.assertTrue(PAGE_NUMBER == True and PAGE_SIZE == True)
				self.assertTrue(len(objects) == STARGATE_DEFAULT_PAGE_SIZE)

		def test_pagination_params(self):
			response = self.client.get('/api/user?page_number=5&page_size=20', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
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
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
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
						self.assertTrue(int(value) == STARGATE_DEFAULT_MAX_PAGE_SIZE)	
						PAGE_SIZE = True

				self.assertTrue(PAGE_NUMBER == True and PAGE_SIZE == True)
				self.assertTrue(len(objects) == STARGATE_DEFAULT_MAX_PAGE_SIZE)

		@classmethod
		def tearDownClass(self):
			with self.app.test_request_context():
				db.session.remove()
				db.drop_all()


if __name__ == '__main__':
    unittest.main()