import os
import unittest
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from stargate.core_api import ResourceManager
from config import ApplicationConfig
from models import User

def init_db(app):
	db = SQLAlchemy()
	db.init_app(app)
	Migrate(app, db)
	return db

def init_app():
	app = Flask(__name__)
	app.config.from_object(ApplicationConfig)
	return app

class TestResource(unittest.TestCase):

		def setUp(self):
			app = init_app()
			app.config['TESTING'] = True
			self.app = app
			self.client = app.test_client()
			self.db = init_db(app)

		def test_resource_registration(self):
			manager = ResourceManager(self.app, flask_sqlalchemy_db = self.db)
			manager.register_resource(User, methods = ['GET'])
			self.assertIsInstance(manager, ResourceManager)


if __name__ == '__main__':
    unittest.main()