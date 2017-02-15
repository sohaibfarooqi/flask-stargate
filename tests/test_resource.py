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

		def setUp(self):
			app = init_app()
			app.config['TESTING'] = True
			self.app = app
			self.client = app.test_client()
			self.db = db

		def test_manager_creation(self):
			manager = ResourceManager(self.app, self.db)
			self.assertIsInstance(manager, ResourceManager)

		def test_resource_creation(self):
			manager = ResourceManager(self.app, self.db)
			
			manager.register_resource(User, methods = ['GET'])
			manager.register_resource(Location, methods = ['GET'])
			manager.register_resource(City, methods = ['GET'])
			
			response = self.client.get('/api/user', headers={"Content-Type": "application/json"})
			self.assertEqual(response._status_code, 200)



if __name__ == '__main__':
    unittest.main()