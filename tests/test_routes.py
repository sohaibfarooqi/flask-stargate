import os
import unittest
from flask import Flask
import sys
import os
sys.path.insert(0,'..')
from stargate.stargate import ResourceManager
from stargate.app.models import User, City, Location
from stargate.app import init_app, db

class TestResource(unittest.TestCase):
		
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

				user.name = "John Baptist"
				user.username = "John91"
				user.age = 19
				user.password = "abcdefg"
				user.email = "johnbaptist@gmail.com"
				user.phone = "923349725618"
				user.pic_url = "/images/pic.jpg"
				user.city_id = city.id
				user.location_id = location.id

				db.session.add(user)
				db.session.commit()
				db.session.flush()
		
		
		def test_get_collection(self):
			response = self.client.get('/api/user', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)
		
		def test_get_instance(self):
			response = self.client.get('/api/user/1', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)

		def test_get_related_instance(self):
			response = self.client.get('/api/user/1/location/1', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)

		def test_get_related_collection(self):
			response = self.client.get('/api/city/1/location', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)

		@classmethod
		def tearDownClass(self):
			with self.app.test_request_context():
				db.session.remove()
				db.drop_all()


if __name__ == '__main__':
    unittest.main()