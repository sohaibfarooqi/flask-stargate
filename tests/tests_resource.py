import unittest
from stargate.views.resource import ResourceAPI
from ..model import User
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

class ResourceAPITest(unittest.TestCase):

		def test_get(self):
			app = Flask(__name__)
			app.config.from_object(ApplicationConfig)
			db = SQLAlchemy()
			db.init_app(app)
			resource_api_view = ResourceAPI.as_view('testingapi', db.session, User, None, 'id')
			
			with app.test_request_context('/?name=Peter'):
    			assert request.path == '/'
    			assert request.args['name'] == 'Peter'

if __name__ == '__main__':
    unittest.main()