import os
import unittest
from flask import Flask, json
import sys
import os
sys.path.insert(0,'..')
from stargate.stargate import Manager
from stargate.app.models import User, City, Location
from stargate.app import init_app, db

class TestFilters(unittest.TestCase):
		
		@classmethod
		def setUpClass(self):
			#Initilize Flask test client
			self.app = init_app(test=True)
			self.client = self.app.test_client()
			#Register Models with manager instance
			self.manager = Manager(self.app, db)
			self.manager.register_resource(User, methods = ['GET'])
			self.manager.register_resource(Location, methods = ['GET'])
			self.manager.register_resource(City, methods = ['GET'])
			#Insert Dummy data for testing
			city = City()
			location = Location()
			user = User()

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

				user.name = "John Doe"
				user.age = 19
				user.username = "John91"
				user.password = "abcdefg"
				user.email = "johnbaptist@gmail.com"
				user.phone = "923349725618"
				user.pic_url = "/images/john.jpg"
				user.city_id = city.id
				user.location_id = location.id

				db.session.add(user)
				db.session.commit()
				
				user.name = "Mark Adams"
				user.age = 20
				user.username = "mark91"
				user.password = "abcdefg"
				user.email = "markadams@gmail.com"
				user.phone = "923349725618"
				user.pic_url = "/images/adam.jpg"
				user.city_id = city.id
				user.location_id = location.id

				db.session.add(user)
				db.session.commit()

				user.name = "Wayne John"
				user.age = 50
				user.username = "wayne91"
				user.password = "abcdefg"
				user.email = "waynejohn@gmail.com"
				user.phone = "923349725618"
				user.pic_url = "/images/wayne.jpg"
				user.city_id = city.id
				user.location_id = location.id

				db.session.add(user)
				db.session.commit()

				user.name = "Muhammad Bin Rashid"
				user.age = 12
				user.username = "muhammadbin91"
				user.password = "abcdefg"
				user.email = "muhammadbinrashid@gmail.com"
				user.phone = "923349725618"
				user.pic_url = "/images/bin.jpg"
				user.city_id = city.id
				user.location_id = location.id

				db.session.add(user)
				db.session.commit()

				user.name = "Vanguard"
				user.age = 23
				user.username = "vanguard91"
				user.password = "abcdefg"
				user.email = "vanguard@gmail.com"
				user.phone = "923349725618"
				user.pic_url = "/images/van.jpg"
				user.city_id = city.id
				user.location_id = location.id

				db.session.add(user)
				db.session.commit()

				db.session.flush()
		
		
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
			filter_1 = dict(name="name", op="in", val=name_list)
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
			
			filter_1 = dict(name="name", op="in", val=["Vanguard", "Wayne John"])
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

		@classmethod
		def tearDownClass(self):
			with self.app.test_request_context():
				db.session.remove()
				db.drop_all()


if __name__ == '__main__':
    unittest.main()