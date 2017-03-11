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
	
	"self": "http://localhost/api/users?page=1&perpage=10",
	"first": "http://localhost/api/users?page=1&perpage=10",
	"last": "http://localhost/api/users?page=10&perpage=10",
	"next": "http://localhost/api/users?page=2&perpage=10",
	"prev": "http://localhost/api/users?page=0&perpage=10"
	
	},
	
	"num_results": 2,
	
	"data": [{
		
		"attributes": {
			"name": "John B",
			"username": "John92",
			"age": 19,
			"email": "johnbapti@gmail.com",
			"password": "abcdefg",
			"phone": "923349725618",
			"created_at": "2017-02-24T17:35:24.223328",
			"pic_url": "/images/pic.jpg"
		},
		
		"id": "1",
		"_link": "http://localhost/api/users/1",
		
		"_embedded": {
			
		"city": {
		"meta":{
		"_type": "to_one",
		"_links": {"self": "http://localhost/api/user/1/city/1"}
		}
		},
			
		"images": {
		"meta":{
		"type": "to_many",
		"_evaluation": "lazy",
		
		"_links": {
		"self":  "http://localhost/api/user/1/images?page=1&perpage=10",
		"first": "http://localhost/api/user/1/images?page=1&perpage=10",
		"last":  "http://localhost/api/user/1/images?page=3&perpage=10",
		"next":  "http://localhost/api/user/1/images?page=2&perpage=10",
		"prev":  "None"
		
		}
		}
		}
		}
	},
	{
	
	"attributes": {
		"name": "John B",
		"username": "John93",
		"age": 19,
		"email": "johnbaptist@gmail.com",
		"password": "abcdefg",
		"phone": "923349725618",
		"created_at": "2017-02-24T17:35:24.223328",
		"pic_url": "/images/pic.jpg"
	},
	
	"id": "2",
	"_link": "http://localhost/api/users/2",

	"_embedded": {
		
	"city": {
	"meta":{
	"_type": "to_one",
	"_link": "http://localhost/api/user/1/city/1"
	}
	},
		
	"images": {
	"meta":{
	"_type": "to_many",
	"_evaluation": "lazy",
	
	"_links": {
	"self": "http://localhost/api/user/1/images?page=1&perpage=10",
	"first": "http://localhost/api/user/1/images?page=1&perpage=10",
	"last": "http://localhost/api/user/1/images?page=2&perpage=10",
	"next": "http://localhost/api/user/1/images?page=2&perpage=10",
	"prev": "None"
	
	}
	}
	}
	}
	}]
	}

	
- ``meta`` will include the response code and response message. 
- ``_links`` contains pagination links i.e first, last, next, prev and self_link.
- ``data`` contains the array of ``User`` objects. Each object has 
	
	- ``attributes``: Resource attributes.
	- ``_link``: Self link.
	- ``id``: Primary key for resource.

- ``_embedded`` keys which represents all resources that are related to ``User``.
	Each related resource will have ``meta`` key which contains: 
	
	- ``_type``: key which represent relationship type i.e. 'to_many' or 'to_one'. 
	
	- ``_evaluation``: key which represent relationship evaluation i.e 'lazy', 'eager'. This is only
		applicable to collection sub resources.
	
	- ``_links``:
		
		- ``self``: self url.
		- ``next``: next page link. Applicable to `lazy` collections only. 
		- ``prev``: prvious page link. Applicable to `lazy` collections only.
		- ``first``: first page link. Applicable to `lazy` collections only.
		- ``last``: last page link. Applicable to `lazy` collections only.

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
		"self": "http://localhost/api/users/1/images?page=1&perpage=10",
		"first": "http://localhost/api/users/1/images?page=1&perpage=10",
		"last": "http://localhost/api/users/1/images?page=10&perpage=10",
		"next": "http://localhost/api/users/1/images?page=2&perpage=10",
		"prev": "http://localhost/api/users/1/images?page=0&perpage=10"
	},
	"data": [{
		"attributes": {
			"title": "profile_pic",
			"path": "/cdnserver/getprofilepic",
			"width": "19",
			"height": "20"
		},
		"id": "1",
		"_link": "http://localhost/api/images/1",
		"_embedded": {
			"image_details": {
				"meta":{
				"type": "to_many",
				"_evaluation": "eager",
				"_link": "/images/2/image_details"
				}
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
		"_link": "http://localhost/api/images/2",
		"_embedded": {
			"image_details": {
				"meta":{
				"type": "to_many",
				"_evaluation": "eager",
				"_link": "/images/2/image_details"
				}
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
			"name": "John B",
			"username": "John93",
			"age": 19,
			"email": "johnbaptist@gmail.com",
			"password": "abcdefg",
			"phone": "923349725618",
			"created_at": "2017-02-24T17:35:24.223328",
			"pic_url": "/images/pic.jpg"
	
		},
		"id": "1",
		"_link": "http://localhost/api/users/1",
		"_embedded": {
			"city": {
			"meta":{
				"type": "to_one",
				"_link": "/user/1/city"
				},
			}
			"images":{
			"meta":{
				"type": "to_many",
				"_evaluation": "lazy"
				"_links": {
					"self": "http://localhost/api/user/1/images?page=1&perpage=10",
					"first": "http://localhost/api/user/1/images?page=1&perpage=10",
					"last": "http://localhost/api/user/1/images?page=3&perpage=10",
					"next": "http://localhost/api/user/1/images?page=2&perpage=10",
					"prev": "None"
				}
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
		"_link": "http://localhost/api/city/1",
		"_embedded": {
			"locations": {
				"_type": "to_many",
				"_evaluation": "eager",
				"_link": "http://localhost/api/city/1/location"
			}
		}
	}
	}