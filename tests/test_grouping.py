import os
import datetime
import unittest
from flask import Flask, json
import sys
import os
sys.path.insert(0,'..')
from stargate.stargate import ResourceManager
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
			user1 = User()
			user2 = User()
			user3 = User()
			user4 = User()
			user5= User()

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

				user1.name = "John Doe"
				user1.age = 19
				user1.username = "John91"
				user1.password = "abcdefg"
				user1.email = "johnbaptist@gmail.com"
				user1.phone = "923349725618"
				user1.pic_url = "/images/john.jpg"
				user1.city_id = city.id
				user1.location_id = location.id

				db.session.add(user1)
				
				user2.name = "Mark Adams"
				user2.age = 20
				user2.username = "mark91"
				user2.password = "abcdefg"
				user2.email = "markadams@gmail.com"
				user2.phone = "923349725618"
				user2.pic_url = "/images/adam.jpg"
				user2.city_id = city.id
				user2.location_id = location.id

				db.session.add(user2)
				
				user3.name = "Wayne John"
				user3.age = 50
				user3.username = "wayne91"
				user3.password = "abcdefg"
				user3.email = "waynejohn@gmail.com"
				user3.phone = "923349725618"
				user3.pic_url = "/images/wayne.jpg"
				user3.city_id = city.id
				user3.location_id = location.id

				db.session.add(user3)
				
				user4.name = "Muhammad Bin Rashid"
				user4.age = 12
				user4.username = "muhammadbin91"
				user4.password = "abcdefg"
				user4.email = "muhammadbinrashid@gmail.com"
				user4.phone = "923349725618"
				user4.pic_url = "/images/bin.jpg"
				user4.city_id = city.id
				user4.location_id = location.id

				db.session.add(user4)
				
				user5.name = "Vanguard"
				user5.age = 23
				user5.username = "vanguard91"
				user5.password = "abcdefg"
				user5.email = "vanguard@gmail.com"
				user5.phone = "923349725618"
				user5.pic_url = "/images/van.jpg"
				user5.city_id = city.id
				user5.location_id = location.id

				db.session.add(user5)
				db.session.commit()
				db.session.flush()
		
		
		def test_single_group(self):
			response = self.client.get('/api/user?group=age', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				age_groups = [user['attributes']['age'] for user in data]
				self.assertTrue(len(age_groups) == len(set(age_groups)))

		def test_multiple_groups(self):
			response = self.client.get('/api/user?group=age,created_at', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				age_groups = [user['attributes']['age'] for user in data]
				time_created = [user['attributes']['created_at'] for user in data]
				age_group_set = set(age_groups)
				time_created_set = set(time_created)
				self.assertTrue((len(age_group_set)== 1 or len(age_groups) == len(age_group_set)) and (len(time_created_set)== 1 or len(time_created) == len(time_created_set)))

		def test_related_model_grouping(self):
			response = self.client.get('/api/user?group=city.id', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				age_groups = [user['attributes']['age'] for user in data]
				self.assertTrue(len(age_groups) == len(set(age_groups)))

		@classmethod
		def tearDownClass(self):
			with self.app.test_request_context():
				db.session.remove()
				db.drop_all()


if __name__ == '__main__':
    unittest.main()