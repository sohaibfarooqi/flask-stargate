POST
====

POST method creates new resource(s) based on data in payload. POST endpoints supports collection 
creation as well as single resource creation.

Url Scheme
----------
Post has only one url scheme:

Resource `User`:

.. code-block:: http

	POST /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json

Simple Post Operation
----------------------

Instance can be created with following request

.. code-block:: http

	POST /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. code-block:: json
	
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


Link already created resources
------------------------------

.. code-block:: http

	POST /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. code-block:: json

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
		"city": {"data":{"id": 1}},
		"location": {"data":{"id": 1}}
		}
	}
	}

Link Related Collection
------------------------
.. code-block:: http

	POST /api/city HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. code-block:: json
	
	{
	"data": {
		"attributes": {
			"title": "Lahore",
			"latitude": 72.8134,
			"longitude": 78.9123,
		},
		"_embedded": {
			"location": {"data":[{"id": 1}, {"id": "2"}]}
			}
		}
	}

Create related instance/collection on fly!
------------------------------------------

.. code-block:: http

	POST /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. code-block:: json
	
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
			"city": { "data":{ "id": 1 } },
			"location": {
				"data":{
					"title": "South Town",
					"latitude": 72.8176,
					"longitude": 79.8143
					}
				}
			}
		}
	}