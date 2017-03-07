# from . import TestSetup
# from flask import json
# import datetime
# from app.models import User, City, Location
# from app import db
# from stargate.const import PaginationConst

# class TestPagination(unittest.TestCase):
		
# 		@classmethod
# 		def setUpClass(self):
# 			super(TestPagination, self).setUp()

# 			#Insert Dummy data for testing
# 			city = City()
# 			location = Location()

# 			with self.app.test_request_context():
# 				db.create_all()
# 				city.title = "Lahore"
# 				city.latitude = 72.813
# 				city.longitude = 78.1987
# 				db.session.add(city)
# 				db.session.commit()
# 				db.session.flush()

# 				location.title = "Johar Town"
# 				location.latitude = 72.813
# 				location.longitude = 78.1987
# 				location.parent_id = -1
# 				location.city_id = city.id
			
# 				db.session.add(location)
# 				db.session.commit()
# 				db.session.flush()
				
# 				user_list = list()
# 				for i in range(0,120):
# 					user = User(name = "John Doe", 
# 								age = 19, 
# 								username = "John91{0}".format(i), 
# 								password = 'abcdef', 
# 								email = "johnbaptist{0}@gmail.com".format(i), 
# 								phone = "923349725618",
# 								pic_url = "/images/john.jpg", 
# 								city_id = city.id, 
# 								location_id = location.id)

# 					user_list.append(user)
				
# 				db.session.bulk_save_objects(user_list)
# 				db.session.commit()
# 				db.session.flush()
		
		
# 		def test_defualt_pagination(self):
# 			response = self.client.get('/api/user', headers={"Content-Type": "application/json"})
# 			content_length = int(response.headers['Content-Length'])

# 			if content_length > 0:
# 				data = json.loads(response.get_data())
# 				objects = data['data']
				
# 				link_header = response.headers['rel']
# 				params = link_header.split('?')[1]
# 				params = params.split('&')
				
# 				PAGE_NUMBER= False
# 				PAGE_SIZE = False
				
# 				for param in params:
# 					key, value = param.split('=')
# 					if key == 'page_number':
# 						self.assertTrue(int(value) == PaginationConst.PAGE_NUMBER)
# 						PAGE_NUMBER = True
					
# 					elif key == 'page_size':
# 						self.assertTrue(int(value) == PaginationConst.PAGE_SIZE)	
# 						PAGE_SIZE = True

# 				self.assertTrue(PAGE_NUMBER == True and PAGE_SIZE == True)
# 				self.assertTrue(len(objects) == PaginationConst.PAGE_SIZE)

# 		def test_pagination_params(self):
# 			response = self.client.get('/api/user?page_number=5&page_size=20', headers={"Content-Type": "application/json"})
# 			content_length = int(response.headers['Content-Length'])

# 			if content_length > 0:
# 				data = json.loads(response.get_data())
# 				objects = data['data']
				
# 				link_header = response.headers['rel']
# 				params = link_header.split('?')[1]
# 				params = params.split('&')
				
# 				PAGE_NUMBER= False
# 				PAGE_SIZE = False
				
# 				for param in params:
# 					key, value = param.split('=')
# 					if key == 'page_number':
# 						self.assertTrue(int(value) == 5)
# 						PAGE_NUMBER = True
					
# 					elif key == 'page_size':
# 						self.assertTrue(int(value) == 20)	
# 						PAGE_SIZE = True

# 				self.assertTrue(PAGE_NUMBER == True and PAGE_SIZE == True)
# 				self.assertTrue(len(objects) == 20)

# 		def test_page_size_limit(self):
# 			response = self.client.get('/api/user?page_number=1&page_size=120', headers={"Content-Type": "application/json"})
# 			content_length = int(response.headers['Content-Length'])

# 			if content_length > 0:
# 				data = json.loads(response.get_data())
# 				objects = data['data']
				
# 				link_header = response.headers['rel']
# 				params = link_header.split('?')[1]
# 				params = params.split('&')
				
# 				PAGE_NUMBER= False
# 				PAGE_SIZE = False
				
# 				for param in params:
# 					key, value = param.split('=')
# 					if key == 'page_number':
# 						self.assertTrue(int(value) == 1)
# 						PAGE_NUMBER = True
					
# 					elif key == 'page_size':
# 						self.assertTrue(int(value) == PaginationConst.MAX_PAGE_SIZE)	
# 						PAGE_SIZE = True

# 				self.assertTrue(PAGE_NUMBER == True and PAGE_SIZE == True)
# 				self.assertTrue(len(objects) == PaginationConst.MAX_PAGE_SIZE)

# 		def test_pagination_links(self):
# 			response = self.client.get('/api/user?page_number=1&page_size=20', headers={"Content-Type": "application/json"})
# 			content_length = int(response.headers['Content-Length'])

# 			if content_length > 0:
				
# 				data = json.loads(response.get_data())
# 				links = data['links']
# 				link_keys = ['first', 'last', 'next', 'prev']
				
# 				self.assertCountEqual(link_keys, links.keys())
				
# 				link_values = [val for val in links.values() if val is not None]

# 				for link in link_values:
# 					params = link.split('?')[1]
# 					params = params.split('&')
					
# 					PAGE_NUMBER = 0
# 					PAGE_SIZE = 0
					
# 					for param in params:
# 						key, value = param.split('=')
# 						if key == 'page_number':
# 							PAGE_NUMBER = int(value)
					
# 						elif key == 'page_size':
# 							PAGE_SIZE = int(value)

# 					pag_response = self.client.get(link, headers={"Content-Type": "application/json"})
# 					link_header = pag_response.headers['rel']
# 					link_params = link_header.split('?')[1]
# 					link_params = link_params.split('&')
					
# 					page_number= 0
# 					page_size = 0
				
# 					for link_param in link_params:
# 						key, value = link_param.split('=')
# 						if key == 'page_number':
# 							page_number = int(value)
					
# 						elif key == 'page_size':	
# 							page_size = int(value)

# 					self.assertTrue(PAGE_NUMBER == page_number and PAGE_SIZE == page_size)
