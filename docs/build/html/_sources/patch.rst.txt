=====
PATCH
=====

Patch method will update attribute(s) of a resource. It can also update related 
collections and related resources.

Url Scheme
----------
Patch has only one url scheme:

Resource `User`:

.. sourcecode:: http

	PATCH /api/user/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

Patch resource attribute(s) like: 

.. sourcecode:: http

	PATCH /api/user/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. sourcecode:: json
	
	{
	"data": {
		"attributes": {
			"username": "John92",
			"password": "12345",
		}
		
		}
	}

Patch relationship with already created resource: 

.. sourcecode:: http

	PATCH /api/user/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. sourcecode:: json
	
	{
	"data": {
		"attributes": {
			"username": "John92",
			"password": "12345",
		},
		"_embedded": {
			"city": {
				"id": 2
			}
		}
	}
	}

Patch relationship with newely created resource: 

.. sourcecode:: http

	PATCH /api/user/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. sourcecode:: json
	
	{
	"data": {
		"_embedded": {
			"city": {
				"title": "Some Famous City",
				"latitude": 78.2134,
				"longitude": 79.8123
			}
		}
	}
	}

Patch to many relationship with already created resources: 

.. sourcecode:: http

	PATCH /api/city/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. sourcecode:: json
	
	{
	"data": {
		"_embedded": {
			"user": [{"id": 1}, {"id": 2}]
		}
	}
	}

Patch with newely created sub resources: 

.. sourcecode:: http

	PATCH /api/city/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. sourcecode:: json
	
	{
	"data": {
		"_embedded": {
			"user": [{
				"name": "John B",
				"username": "John91",
				"age": 19,
				"email": "johnbaptist@gmail.com",
				"password": "abcdefg",
				"phone": "923349725618",
				"created_at": "2017-02-24T17:35:24.223328",
				"pic_url": "/images/pic.jpg"}, 
				{"id": 2}]
		}
	}
	}

.. note:: Patch doesnot delete any sub resources that are not specified in payload.