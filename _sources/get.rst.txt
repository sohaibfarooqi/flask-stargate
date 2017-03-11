===
GET
===

GET request can be use to fetch an instance or collection. 

Collections
===========

Collection can be queried in two different ways:

Primary Resource `User`:

.. sourcecode:: http

	GET /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json
	

Related Resource `Images`:

.. sourcecode:: http

	GET /api/user/1/images HTTP/1.1
	Host: client.com 
	Accept: application/json

Pagination
-----------
Pagination on collections can be simply performed as follows:

.. sourcecode:: http

	GET /api/user?page_number=1&page_size=20 HTTP/1.1
	Host: client.com 
	Accept: application/json

This will yield response

.. code-block:: http
	
		HTTP/1.1 200 OK
		Content-Type: application/json
	
		{
		"meta": {
			"status_code": 200,
			"message": "Ok."
		},
		"num_results": 120,
		"_links":{
			"last": "http://localhost:5000/api/user?page_number=12&page_size=10",
			"next": "http://localhost:5000/api/user?page_number=2&page_size=10",
			"first": "http://localhost:5000/api/user?page_number=1&page_size=10",
			"prev": "None"
			}
		}

Pagination links will only appear if applicable otherwise ``None`` will be the value.
Default page_size is 10 and Default page_number is 1. 
Max page_size is 100.  

Partial Response
-----------------
Partial response can be done in two ways:
 
	1. Selective attributes

	.. sourcecode:: http

		GET /api/user?fields=name,age HTTP/1.1
		Host: client.com 
		Accept: application/json

	This will yield response:

	.. code-block:: http
	
		HTTP/1.1 200 OK
		Content-Type: application/json
	
		{
		"meta": {
			"status_code": 200,
			"message": "Ok."
		},
		"num_results": 1,
		"data": [{
			"_link": "http://localhost:5000/api/user/1",
			"id": 1,
			"attributes": {
				"age": 19,
				"name": "John Doe"
				}
			}]

		}


	2. Excluding attributes

	.. sourcecode:: http

		GET /api/user?exclude=name,age HTTP/1.1
		Host: client.com 
		Accept: application/json


	This will yield response:

	.. code-block:: http

		HTTP/1.1 200 OK
		Content-Type: application/json

		{
		"meta": {
			"status_code": 200,
			"message": "Ok."
			},
		"num_results": 1,
		"data": [{
			"_link": "http://localhost:5000/api/user/1",
			"id": 1,
			"attributes": {
			"username": "John91",
			"email": "johnbaptist@gmail.com",
			"password": "abcdefg",
			"phone": "923349725618",
			"created_at": "2017-02-24T17:35:24.223328",
			"pic_url": "/images/pic.jpg"
			}
			}]

		}


Resource Expansion
------------------
Related resources can be expanded in a following manner:

.. code-block:: http

	GET /api/user?expand=location HTTP/1.1
	Host: client.com 
	Accept: application/json

This will yield response:

.. code-block:: http

	HTTP/1.1 200 OK
	Content-Type: application/json

	{
	"meta": {
		"status_code": 200,
		"message": "Ok."
		},
	"num_results": 1,
	"data": [{
	"_embedded":{
		"location":{
		"meta":{
			"_link":{
			"self":"http://localhost:5000/api/user/1/location/1"
			},
			"_type": "to_one"
		},
		"data":{
			"id": 1,
			"_link": "http://localhost:5000/api/location/1"
			"attributes":{
			"title": "Johar Town",
			"latitude": 72.8176,
			"longitude": 78.91823,
			"created_at": "2017-02-24T17:35:24.223328",
			"parent_id": -1
			}
		}
		},
		"city":{
		"meta":{
			"_link":{
			"self":"http://localhost:5000/api/user/1/city/1"
			},
			"_type": "to_one"
		}
	}
	},

	"_link": "http://localhost:5000/api/user/1",
	"id": 1,
	"attributes": {
	"username": "John91",
	"email": "johnbaptist@gmail.com",
	"password": "abcdefg",
	"phone": "923349725618",
	"created_at": "2017-02-24T17:35:24.223328",
	"pic_url": "/images/pic.jpg"
	}
	}]

	}

By default related resources will only have ``_link(s)`` and ``_type``. Link can be used to 
get full resource representation. Type defines if relation is `to_many` or `to_one`.

You can also specify selective fields on related resources. Primary key and link to self are always
included.

.. code-block:: http

	GET /api/user?expand=location(latitude,longitude) HTTP/1.1
	Host: client.com 
	Accept: application/json

This will yield response:

.. code-block:: http
	
	HTTP/1.1 200 OK
	Content-Type: application/json

	{
	"meta": {
		"status_code": 200,
		"message": "Ok."
		},
	"num_results": 1,
	"data": [{
	"_embedded":{
		"location":{
		"meta":{
			"_link":{
			"self":"http://localhost:5000/api/user/1/location/1"
			},
			"_type": "to_one"
		},
		"data":{
			"id": 1,
			"_link": "http://localhost:5000/api/location/1"
			"attributes":{
			"latitude": 72.8176,
			"longitude": 78.91823,
			}
		}
		},
		"city":{
		"meta":{
			"_link":{
			"self":"http://localhost:5000/api/user/1/city/1"
			},
			"_type": "to_one"
		}
	}
	},

	"_link": "http://localhost:5000/api/user/1",
	"id": 1,
	"attributes": {
	"username": "John91",
	"email": "johnbaptist@gmail.com",
	"password": "abcdefg",
	"phone": "923349725618",
	"created_at": "2017-02-24T17:35:24.223328",
	"pic_url": "/images/pic.jpg"
	}
	}]

	}

Filters
--------
Collections can be filtered

.. sourcecode:: http

	GET /api/user?filters=[{"name":"name","op":"like","val":"john"}] HTTP/1.1
	Host: client.com 
	Accept: application/json

This will perform SQL operation ``name LIKE "john"``

Query Format is: 

.. sourcecode:: json

	{"name": "attribute", "op": "Operator", "val": "compare against"} 

You can also nest filters with logical boolean operators

.. sourcecode:: json

	[{"or":[{"name":"age","op":"ge","val":"19"}, {"name":"city","op":"eq","val":"1"}]}]

This will result in SQL Expression ``age > 19 OR city=1``

Sorting
-------
Sorting can be done like

.. sourcecode:: http

	GET /api/user?sort=updated_at-,name+ HTTP/1.1
	Host: client.com 
	Accept: application/json

This will perform ``updated_at DESE, name ASC``. This will have users who were updated
recently sorted alphabetically

Grouping
--------
Grouping example:

.. sourcecode:: http

	GET /api/user?group=created_at,age HTTP/1.1
	Host: client.com 
	Accept: application/json

This will perform ``GROUP BY created_at, age``. This will group the users who were created 
at same date/time and have same age.

Instance
========

Instances can be queried in two different ways:

Primary Resource `User`:

.. sourcecode:: http

	GET /api/user/1 HTTP/1.1
	Host: client.com 
	Accept: application/json
	
will yield response:

.. code-block:: http
	
	HTTP/1.1 200 OK
	Content-Type: application/json

	{
	"data": {
	"id": 1,
	"_embedded": {
		"city": {
		"meta": {
			"_links": {
			"self": "http://localhost:5000/api/user/1/city/1"
				},
			"_type": "to_one"
			}
		},
		"location": {
		"meta": {
			"_links": {
			"self": "http://localhost:5000/api/user/1/location/1"
				},
			"_type": "to_one"
			}
		}
	},
	"_link": "http://localhost:5000/api/user/1",
	"attributes": {
		"name": "John Baptist",
		"password": "abcdefg",
		"updated_at": "None",
		"age": 19,
		"email": "johnbaptist@gmail.com",
		"created_at": "2017-03-11T14:04:22.487051",
		"phone": "923349725618",
		"pic_url": "/images/pic.jpg",
		"username": "John91"
	}

	},
	"meta": {
		"message": "Ok.",
		"status_code": 200
		}
	}

Related Resource `city`:

.. sourcecode:: http

	GET /api/user/1/location/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

Will yield response:

.. code-block:: http
	
	HTTP/1.1 200 OK
	Content-Type: application/json

	{
	"meta": {
		"message": "Ok.",
		"status_code": 200
	},
	"data": {
	"_embedded": {
		"city": {
		"meta": {
			"_links": {
				"self": "http://localhost:5000/api/location/1/city/1"
			},
			"_type": "to_one"
			}
		}
		},
		"_link": "http://localhost:5000/api/location/1",
		"attributes": {
			"created_at": "2017-03-11T14:15:31.295018",
			"longitude": 78.1987,
			"title": "Johar Town",
			"parent_id": -1,
			"latitude": 72.813,
			"updated_at": "None"
		},
		"id": 1
	}
	}


``fields``, ``exclude`` and ``expand`` can be applied to instances too.
