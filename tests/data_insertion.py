from app.models import User, City, Location
from app import db

def insert_pagination_data(test_client):
			city = City()
			location = Location()

			with test_client.test_request_context():
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
				
				user_list = list()
				for i in range(0,120):
					user = User(name = "John Doe", 
								age = 19, 
								username = "John91{0}".format(i), 
								password = 'abcdef', 
								email = "johnbaptist{0}@gmail.com".format(i), 
								phone = "923349725618",
								pic_url = "/images/john.jpg", 
								city_id = city.id, 
								location_id = location.id)

					user_list.append(user)
				
				db.session.bulk_save_objects(user_list)
				db.session.commit()
				db.session.flush()

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

def insert_filteration_data(test_client):
		city = City()
		location = Location()
		
		user1 = User()
		user2 = User()
		user3 = User()
		user4 = User()
		user5 = User()

		with test_client.test_request_context():
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
			db.session.commit()
			
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
			db.session.commit()

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
			db.session.commit()

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
			db.session.commit()

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