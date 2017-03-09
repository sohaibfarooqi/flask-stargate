import unittest
from flask import Flask, json, request
import sys
import os
sys.path.insert(0,'..')
from stargate import Manager
from stargate.resource_info import resource_info
from app.models import User, City, Location, TestPrimaryKey
from app import init_app, db
from .data_insertion import insert_simple_test_data, insert_filteration_data, insert_pagination_data
from functools import wraps 

"""Test Decorator"""
def auth_key_header(func):
    @wraps(func)
    def new_func(*args, **kw):
        header = request.headers.get('X-AUTH_KEY')
        if header != '1234567':
        	raise ValueError("Invalid AUTH_KEY")
        return func(*args, **kw)
    return new_func

class TestSetup(unittest.TestCase):
		
		@classmethod
		def setUpClass(self):
			#Initilize Flask test client
			self.app = init_app(test=True)
			self.client = self.app.test_client()
			#Initilize Manager object
			self.manager = Manager(self.app, db)
			#Register resources with Manager instance
			self.manager.register_resource(User, methods = ['GET', 'POST'])
			self.manager.register_resource(Location, methods = ['GET', 'POST'])
			self.manager.register_resource(City, methods = ['GET', 'POST'])

			with self.app.test_request_context():
				db.create_all()
		
		@classmethod
		def tearDownClass(self):
			with self.app.test_request_context():
				db.session.remove()
				db.drop_all()
				resource_info.created_managers.clear()
			
class SimpleTestBase(TestSetup):
	
	@classmethod
	def setUpClass(self):
		super(SimpleTestBase, self).setUpClass()
		#Insert Simple Testing Data.
		insert_simple_test_data(self.app)
			
		@classmethod
		def tearDownClass(self):
			super(SimpleTestBase, self).tearDownClass()
			

class DescriptiveTestBase(TestSetup):
	
	@classmethod
	def setUpClass(self):
		super(DescriptiveTestBase, self).setUpClass()
		
		insert_filteration_data(self.app)
			
		@classmethod
		def tearDownClass(self):
			super(DescriptiveTestBase, self).tearDownClass()

class PaginatedTestBase(TestSetup):
	
	@classmethod
	def setUpClass(self):
		super(PaginatedTestBase, self).setUpClass()
		
		#Insert Simple Testing Data.
		insert_pagination_data(self.app)
			
		@classmethod
		def tearDownClass(self):
			super(PaginatedTestBase, self).tearDownClass()

class ManagerTestBase(unittest.TestCase):
	
	@classmethod
	def setUpClass(self):
		#Initilize Flask test client
		self.app = init_app(test=True)
		self.client = self.app.test_client()
		#Initilize Manager object
		self.manager = Manager(self.app, db)
		#Register resources with Manager instance
		self.manager.register_resource(User, endpoint = 'mycustomcollection', methods = ['GET'])
		self.manager.register_resource(Location, fields = ['latitude','longitude'])
		self.manager.register_resource(City, url_prefix = '/v1', exclude = ['latitude','longitude'])
		self.manager.register_resource(TestPrimaryKey, endpoint = 'testprimarykey', decorators = [auth_key_header], primary_key = 'ser_id')

		insert_pagination_data(self.app)
	
	@classmethod
	def tearDownClass(self):
		with self.app.test_request_context():
			db.session.remove()
			db.drop_all()
			resource_info.created_managers.clear()

if __name__ == '__main__':
    unittest.main()