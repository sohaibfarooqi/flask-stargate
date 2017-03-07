import unittest
from flask import Flask, json
import sys
import os
sys.path.insert(0,'..')
from stargate import Manager
from stargate.resource_info import resource_info
from app.models import User, City, Location
from app import init_app, db

def insert_simple_test_data(test_client):
	
	with test_client.test_request_context():
		db.create_all()
		#Insert Dummy data for testing
		city = City()
		location = Location()
		user = User()

		city.title = "Lahore"
		city.latitude = 72.813
		city.longitude = 78.1987

		db.session.add(city)
		db.session.flush()
		db.session.commit()
			

		location.title = "Johar Town"
		location.latitude = 72.813
		location.longitude = 78.1987
		location.parent_id = -1
		location.city_id = city.id
	
		db.session.add(location)
		db.session.flush()
		db.session.commit()
			

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
		db.session.flush()
		db.session.commit()

class TestSetup(unittest.TestCase):
		
		@classmethod
		def setUpClass(self):
			#Initilize Flask test client
			self.app = init_app(test=True)
			self.client = self.app.test_client()
			#Initilize Manager object
			self.manager = Manager(self.app, db)

			self.manager.register_resource(User, methods = ['GET'])
			self.manager.register_resource(Location, methods = ['GET'])
			self.manager.register_resource(City, methods = ['GET'])
			insert_simple_test_data(self.app)
			
		@classmethod
		def tearDownClass(self):
			with self.app.test_request_context():
				db.session.remove()
				db.drop_all()
				resource_info.created_managers.clear()
			

if __name__ == '__main__':
    unittest.main()