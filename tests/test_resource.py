import os
import unittest
from flask import Flask
import sys
import os
sys.path.insert(0,'..')
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from stargate.stargate import ResourceManager
from stargate.models import User
from stargate.app import init_app, init_db

class TestResource(unittest.TestCase):

		def setUp(self):
			app = init_app()
			app.config['TESTING'] = True
			self.app = app
			self.client = app.test_client()
			self.db = init_db(app)

		def test_manager_creation(self):
			manager = ResourceManager(self.app, self.db)
			self.assertIsInstance(manager, ResourceManager)


if __name__ == '__main__':
    unittest.main()