# from sqlalchemy import inspect
# from sqlalchemy.exc import NoInspectionAvailable
# from . import TestSetup
# from flask import json
# import datetime
# from app.models import User, City, Location
# from app import db


# def foreign_key_columns(model):
#     try:
#         inspector = inspect(model)
#     except NoInspectionAvailable:
#         inspector = class_mapper(model)
#     all_columns = inspector.columns
#     all_fks = [c for c in all_columns if c.foreign_keys]
#     return [column.name for column in all_fks]

# class TestQueryOptions(TestSetup):
		
# 		@classmethod
# 		def setUpClass(self):
# 			super(TestQueryOptions, self).setUp()

# 			#Insert Dummy data for testing
# 			city = City()
# 			location = Location()
# 			user1 = User()
# 			user2 = User()
# 			user3 = User()
# 			user4 = User()
# 			user5= User()

# 			with self.app.test_request_context():
# 				db.create_all()
# 				city.title = "Lahore"
# 				city.latitude = 72.813
# 				city.longitude = 78.1987
# 				db.session.add(city)
# 				db.session.commit()
# 				db.session.flush()

# 				location.title = "Johar Town"
# 				location.latitude = 72.813
# 				location.longitude = 78.1987
# 				location.parent_id = -1
# 				location.city_id = city.id
			
# 				db.session.add(location)
# 				db.session.commit()
# 				db.session.flush()

# 				user1.name = "John Doe"
# 				user1.age = 19
# 				user1.username = "John91"
# 				user1.password = "abcdefg"
# 				user1.email = "johnbaptist@gmail.com"
# 				user1.phone = "923349725618"
# 				user1.pic_url = "/images/john.jpg"
# 				user1.city_id = city.id
# 				user1.location_id = location.id

# 				db.session.add(user1)
				
# 				user2.name = "Mark Adams"
# 				user2.age = 20
# 				user2.username = "mark91"
# 				user2.password = "abcdefg"
# 				user2.email = "markadams@gmail.com"
# 				user2.phone = "923349725618"
# 				user2.pic_url = "/images/adam.jpg"
# 				user2.city_id = city.id
# 				user2.location_id = location.id

# 				db.session.add(user2)
				
# 				user3.name = "Wayne John"
# 				user3.age = 50
# 				user3.username = "wayne91"
# 				user3.password = "abcdefg"
# 				user3.email = "waynejohn@gmail.com"
# 				user3.phone = "923349725618"
# 				user3.pic_url = "/images/wayne.jpg"
# 				user3.city_id = city.id
# 				user3.location_id = location.id

# 				db.session.add(user3)
				
# 				user4.name = "Muhammad Bin Rashid"
# 				user4.age = 12
# 				user4.username = "muhammadbin91"
# 				user4.password = "abcdefg"
# 				user4.email = "muhammadbinrashid@gmail.com"
# 				user4.phone = "923349725618"
# 				user4.pic_url = "/images/bin.jpg"
# 				user4.city_id = city.id
# 				user4.location_id = location.id

# 				db.session.add(user4)
				
# 				user5.name = "Vanguard"
# 				user5.age = 23
# 				user5.username = "vanguard91"
# 				user5.password = "abcdefg"
# 				user5.email = "vanguard@gmail.com"
# 				user5.phone = "923349725618"
# 				user5.pic_url = "/images/van.jpg"
# 				user5.city_id = city.id
# 				user5.location_id = location.id

# 				db.session.add(user5)
# 				db.session.commit()
# 				db.session.flush()
		
		
# 		def test_field_selection(self):
# 			fields = ['name', 'age']
# 			response = self.client.get('/api/user?field=name,age', headers={"Content-Type": "application/json"})
# 			content_length = int(response.headers['Content-Length'])

# 			if content_length > 0:
# 				data = json.loads(response.get_data())
# 				data = data['data']
# 				for key in data:
# 					keys = list(key['attributes'].keys())
# 					self.assertCountEqual(keys, fields)
				
# 		def test_field_exclusion(self):
# 			exclude = ['name', 'age']
# 			response = self.client.get('/api/user?exclude=name,age', headers={"Content-Type": "application/json"})
# 			content_length = int(response.headers['Content-Length'])

# 			if content_length > 0:
# 				data = json.loads(response.get_data())
# 				data = data['data']
# 				for key in data:
# 					keys = list(key['attributes'].keys())
# 					self.assertNotIn(exclude, keys)

# 		def test_resource_expansion(self):
# 			response = self.client.get('/api/user?expand=location', headers={"Content-Type": "application/json"})
# 			content_length = int(response.headers['Content-Length'])

# 			if content_length > 0:
# 				data = json.loads(response.get_data())
# 				data = data['data']
# 				all_attrs = [key for key in Location.__table__.columns.keys() if key != 'id' and key not in foreign_key_columns(Location)]
# 				for key in data:
# 					keys = list(key['_embedded']['location']['data']['attributes'].keys())
# 					self.assertCountEqual(all_attrs, keys)

# 		def test_resource_expansion_with_fields(self):
# 			fields = ['latitude', 'longitude']
# 			response = self.client.get('/api/user?expand=location(latitude, longitude)', headers={"Content-Type": "application/json"})
# 			content_length = int(response.headers['Content-Length'])

# 			if content_length > 0:
# 				data = json.loads(response.get_data())
# 				data = data['data']
# 				for key in data:
# 					keys = list(key['_embedded']['location']['data']['attributes'].keys())
# 					for attr in keys:
# 						self.assertIn(attr, fields)
