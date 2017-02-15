==============
Response Style
==============
Response format are grouped in collection and instance response. Both will have a different 
respresentation for client. All request options can be applied to either collection resource or 
instance resource, provided it make sense to it. For example pagination params don't make any 
sense if you are requesting for a resource with a specified id. So pagination params will be ignored
in case of instance resoure.

Collection Representation
-------------------------
By default GET request to any resource will yield response in following format.

Simple collection
.................

.. sourcecode:: http

	GET /api/user HTTP/1.1
	Host: client.com 
	Accept: application/json

.. sourcecode:: http

	HTTP/1.1 200 OK
   	Content-Type: application/json
	
	{
	"meta": {
		"status": 200,
		"message": "Ok."
	},
	"_links": {
		"self": "/api/users?page=1&perpage=10",
		"first": "/api/users?page=1&perpage=10",
		"last": "/api/users?page=10&perpage=10",
		"next": "/api/users?page=2&perpage=10",
		"previous": "/api/users?page=0&perpage=10"
	},
	"data": [{
		"attributes": {
			"name": "John",
			"age": "19",
			"username": "John91",
			"sex": "M"
		},
		"id": "1",
		"_embedded": {
			"city": {
				"type": "TO_ONE",
				"_link": "/user/1/city"
			},
			"images": {
				"type": "TO_MANY",
				"_link": "/user/1/images"
			}
		}
	}, {
		"attributes": {
			"name": "John Agha",
			"age": "23",
			"username": "John92",
			"sex": "M"
		},
		"id": "2",
		"_embedded": {
			"city": {
				"type": "TO_ONE",
				"_link": "/user/1/city"
			},
			"images": {
				"type": "TO_MANY",
				"_link": "/user/1/images"
			}
		},
		"num_results": 2
	}]
	}

	
``meta`` will include the response code and message. ``_links`` contains pagination links.
``data`` contains the array of ``User`` objects. Each object has ``attributes`` and ``id`` keys.
It further includes ``_embedded`` keys which represents all resources that are related to ``User``.
Each related resource will ``type`` key which represent relationship type and ``_link`` key to get 
the full resource. 

.. note:: All related resources will only have relationship type and link to get the full resource. 
		  If you want to get full resource representation in ``/user`` endpoint, Please specify 
		  ``expand=images,city`` in request query string. For more information see resource expansion.

Related Collection
..................
Related collection will have a url format like ``/<primary_resource>/<id>/<related_resource>``.
It will yield a format similar to simple collection except ``_embedded`` will now have related collections'
relationships.

.. sourcecode:: http

	GET /api/user/1/images HTTP/1.1
	Host: client.com 
	Accept: application/json

.. sourcecode:: http

	HTTP/1.1 200 OK
   	Content-Type: application/json
	
	{
	"meta": {
		"status": 200,
		"message": "Ok."
	},
	"_links": {
		"self": "/api/users/1/images?page=1&perpage=10",
		"first": "/api/users1/images?page=1&perpage=10",
		"last": "/api/users1/images?page=10&perpage=10",
		"next": "/api/users1/images?page=2&perpage=10",
		"previous": "/api/users1/images?page=0&perpage=10"
	},
	"data": [{
		"attributes": {
			"title": "profile_pic",
			"path": "/cdnserver/getprofilepic",
			"width": "19",
			"height": "20"
		},
		"id": "1",
		"_embedded": {
			"image_details": {
				"type": "TO_MANY",
				"_link": "/images/2/image_details"
			}
		}
	}, {
		"attributes": {
			"title": "cover_pic",
			"path": "/cdnserver/getcoverpic",
			"width": "190",
			"height": "80"
		},
		"id": "2",
		"_embedded": {
			"image_details": {
				"type": "TO_MANY",
				"_link": "/images/2/image_details"
			}
		},
		"num_results": 2
	}]
	}


Instance Representation
-----------------------

Simple Instance
...............

.. sourcecode:: http

	GET /api/user/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

.. sourcecode:: http

	HTTP/1.1 200 OK
   	Content-Type: application/json

	{
	"meta": {
		"status": 200,
		"message": "Ok."
	},
	"data": {
		"attributes": {
			"name": "John",
			"age": "19",
			"username": "John91",
			"sex": "M"
		},
		"id": "1",
		"_embedded": {
			"city": {
				"type": "TO_ONE",
				"_link": "/user/1/city"
			},
			"images": {
				"type": "TO_MANY",
				"_link": "/user/1/images"
			}
		}
	}
	}

Instance representation has no ``_links`` (pagination links) and ``num_results``.
Related resources expansion can be done just like in collection resources.

Related Instance
................


.. sourcecode:: http

	GET /api/user/1/city/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

.. sourcecode:: http

	HTTP/1.1 200 OK
   	Content-Type: application/json

	{
	"meta": {
		"status": 200,
		"message": "Ok."
	},
	"data": {
		"attributes": {
			"title": "Lahore",
			"latitude": "72.81654",
			"longitude": "78.1907866"
		},
		"id": "1",
		"_embedded": {
			"locations": {
				"type": "TO_MANY",
				"_link": "/city/1/location"
			}
		}
	}
	}