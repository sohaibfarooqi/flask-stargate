POST
====

POST method creates new resource(s) based on data in payload. POST endpoints supports collection 
creation as well as single resource creation.

Url Scheme
----------
Post has only one url scheme:

Resource `User`:

.. sourcecode:: http

	POST /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json

Creating Instance
-----------------

Single instance can be created with following request

.. sourcecode:: http

	POST /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. sourcecode:: json
	
	{
	"data": {
		"attributes": {
			"name": "John B",
			"username": "John91",
			"age": 19,
			"email": "johnbaptist@gmail.com",
			"password": "abcdefg",
			"phone": "923349725618",
			"created_at": "2017-02-24T17:35:24.223328",
			"pic_url": "/images/pic.jpg"
		}
		
		}
	}



You can also link an already created instance:

.. sourcecode:: http

	POST /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. sourcecode:: json
	
	{
	"data": {
		"attributes": {
			"name": "John B",
			"username": "John91",
			"age": 19,
			"email": "johnbaptist@gmail.com",
			"password": "abcdefg",
			"phone": "923349725618",
			"created_at": "2017-02-24T17:35:24.223328",
			"pic_url": "/images/pic.jpg"
		},
		"_embedded": {
			"city": {
				"id": 1
			},
			"location": {
				"id": 1
			}
		}
	}
	}


Link resources on the fly!:

.. sourcecode:: http

	POST /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. sourcecode:: json
	
	{
	"data": {
		"attributes": {
			"name": "John B",
			"username": "John91",
			"age": 19,
			"email": "johnbaptist@gmail.com",
			"password": "abcdefg",
			"phone": "923349725618",
			"created_at": "2017-02-24T17:35:24.223328",
			"pic_url": "/images/pic.jpg"
		},
		"_embedded": {
			"city": {
				"id": 1
			},
			"location": {
				"title": "South Town",
				"latitude": 72.8176,
				"longitude": 79.8143
			}
		}
	}
	}

Creating Collection
--------------------

Create list of resources:

.. sourcecode:: http

	POST /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. sourcecode:: json
	
	{
	"data": [{
		"attributes": {
			"name": "John B",
			"username": "John91",
			"age": 19,
			"email": "johnbaptist@gmail.com",
			"password": "abcdefg",
			"phone": "923349725618",
			"created_at": "2017-02-24T17:35:24.223328",
			"pic_url": "/images/pic.jpg"
		},
		"_embedded": {
			"city": {
				"id": 1
			},
			"location": {
				"title": "South Town",
				"latitude": 72.8176,
				"longitude": 79.8143
			}
		}
	},
	{
		"attributes": {
			"name": "John B",
			"username": "John91",
			"age": 19,
			"email": "johnbaptist@gmail.com",
			"password": "abcdefg",
			"phone": "923349725618",
			"created_at": "2017-02-24T17:35:24.223328",
			"pic_url": "/images/pic.jpg"
		},
		"_embedded": {
			"city": {
				"id": 1
			},
			"location": {
				"id": 1
			}
		}
	}]
	}

