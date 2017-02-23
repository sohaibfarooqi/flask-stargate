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
		
		
		def test_to_many_type(self):
			response = self.client.get('/api/city/1', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				relation_type = data['data']['_embedded']['user']['meta']['_type']
				self.assertEqual(relation_type, 'TO_MANY')

		def test_to_one_type(self):
			response = self.client.get('/api/user/1', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				relation_type = data['data']['_embedded']['city']['meta']['_type']
				self.assertEqual(relation_type, 'TO_ONE')

		def test_embedded_self_link(self):
			#TO_ONE
			response = self.client.get('/api/user/1', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				self_rel = data['data']['_embedded']['city']['meta']['_links']['self']
				self.assertEqual(self_rel, 'http://localhost/api/user/1/city/1')

			#TO_MANY
			response = self.client.get('/api/city/1', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				self_rel = data['data']['_embedded']['user']['meta']['_links']['self']
				#LAZY
				self.assertEqual(self_rel, 'http://localhost/api/city/1/user?page_number=1&page_size=10')
				#EAGER
				self_rel = data['data']['_embedded']['location']['meta']['_links']['self']
				self.assertEqual(self_rel, 'http://localhost/api/city/1/location')
				
		def test_embedded_pagination_links(self):
			response = self.client.get('/api/city/1?expand=user', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
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
					

		@classmethod
		def tearDownClass(self):
			with self.app.test_request_context():
				db.session.remove()
				db.drop_all()


if __name__ == '__main__':
    unittest.main()