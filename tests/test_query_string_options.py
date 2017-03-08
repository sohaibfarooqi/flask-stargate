from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable
from . import DescriptiveTestBase
from flask import json
import datetime
from app.models import User, City, Location
from app import db


def foreign_key_columns(model):
    try:
        inspector = inspect(model)
    except NoInspectionAvailable:
        inspector = class_mapper(model)
    all_columns = inspector.columns
    all_fks = [c for c in all_columns if c.foreign_keys]
    return [column.name for column in all_fks]

class TestQueryOptions(DescriptiveTestBase):
		
		@classmethod
		def setUpClass(self):
			super(TestQueryOptions, self).setUpClass()

		def test_field_selection(self):
			fields = ['name', 'age']
			response = self.client.get('/api/user?field=name,age', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				for key in data:
					keys = list(key['attributes'].keys())
					self.assertCountEqual(keys, fields)
				
		def test_field_exclusion(self):
			exclude = ['name', 'age']
			response = self.client.get('/api/user?exclude=name,age', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				for key in data:
					keys = list(key['attributes'].keys())
					self.assertNotIn(exclude, keys)

		def test_resource_expansion(self):
			response = self.client.get('/api/user?expand=location', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				all_attrs = [key for key in Location.__table__.columns.keys() if key != 'id' and key not in foreign_key_columns(Location)]
				for key in data:
					keys = list(key['_embedded']['location']['data']['attributes'].keys())
					self.assertCountEqual(all_attrs, keys)

		def test_resource_expansion_with_fields(self):
			fields = ['latitude', 'longitude']
			response = self.client.get('/api/user?expand=location(latitude, longitude)', headers={"Content-Type": "application/json"})
			content_length = int(response.headers['Content-Length'])

			if content_length > 0:
				data = json.loads(response.get_data())
				data = data['data']
				for key in data:
					keys = list(key['_embedded']['location']['data']['attributes'].keys())
					for attr in keys:
						self.assertIn(attr, fields)
