POST
====

POST method creates new resource and sub resources based on data in payload. 

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

	POST /api/city HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. code-block:: json
	
	{
	"data": {
		"attributes": {
			"title": "Lahore",
			"latitude": 72.8176,
			"longitude": 79.2998
			}
		
		}
	}

will yield response:

.. code-block:: http
	
	HTTP/1.1 201 CREATED
	Content-Type: application/json

	{
	"data": {
		"_embedded": {
			"location": {},
			"user": {}
		},
		"id": 1,
		"_link": "http://localhost:5000/api/city/1",
		"attributes": {
			"title": "Lahore",
			"updated_at": "None",
			"latitude": 72.8176,
			"longitude": 79.2998
			"created_at": "2017-03-11T14:41:47.140392"
		}
	},
	"meta": {
		"message": "Created",
		"status_code": 201
	}
	}

Link already created resources
------------------------------

.. code-block:: http

	POST /api/location HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. code-block:: json

	{
	"data": {
		"attributes": {
			"title": "Johar Town",
			"latitude": 72.8176,
			"longitude": 79.2998,
			"parent_id": -1
		},
	"_embedded":{
		"city":{"data":{"id": 1}}
		}
	}

	}

.. code-block:: http

	HTTP/1.1 201 CREATED
	Content-Type: application/json
	
	{
	"meta": {
		"status_code": 201,
		"message": "Created"
	},
	"data": {
		"_embedded": {
		"city": {
		"meta": {
		"_links": {
		"self": "http://localhost:5000/api/location/1/city/1"
		},
		"_type": "to_one"
		},
		"data": {
			"id": 1,
			"_link": "http://localhost:5000/api/city/1",
			"attributes": {
			"created_at": "2017-03-11T14:53:19.906067",
			"latitude": 72.8176,
			"longitude": 79.2998,
			"title": "Lahore",
			"updated_at": "None"
			}
			}
			}
		},
		"id": 1,
		"_link": "http://localhost:5000/api/location/1",
		"attributes": {
			"created_at": "2017-03-11T14:53:19.922127",
			"parent_id": -1,
			"latitude": 72.8176,
			"longitude": 79.2998,
			"title": "Johar Town",
			"updated_at": "None"
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

.. code-block:: http

	HTTP/1.1 201 CREATED
	Content-Type: application/json

	{
	"meta": {
		"message": "Created",
		"status_code": 201
	},
	"data": {
	"_link": "http://localhost:5000/api/city/1",
	"id": 1,
		"_embedded": {
		"location": {
		"meta": {
		"_evaluation": "eager",
		"_type": "to_many",
		"_links": {
		"self": "http://localhost:5000/api/city/1/location"
			}
		},
		"data": [{
			"_link": "http://localhost:5000/api/location/1",
			"id": 1,
			"attributes": {
				"parent_id": -1,
				"title": "Wapda Town",
				"longitude": 79.2998,
				"latitude": 72.8176,
				"created_at": "2017-03-11T15:10:55.885073",
				"updated_at": "2017-03-11T15:10:55.914766"
			}
		}, 
			{
			"_link": "http://localhost:5000/api/location/2",
			"id": 2,
			"attributes": {
				"parent_id": -1,
				"title": "Wapda Town",
				"longitude": 79.2998,
				"latitude": 72.8176,
				"created_at": "2017-03-11T15:10:55.905809",
				"updated_at": "2017-03-11T15:10:55.914766"
			}
		}]
			},
			"user": {}
		},
		"attributes": {
			"title": "Lahore",
			"latitude": 72.8134,
			"longitude": 78.9123,
			"created_at": "2017-03-11T15:10:55.914766",
			"updated_at": "None",
			}
		}
	}

Create related instance/collection on fly!
------------------------------------------

.. code-block:: http

	POST /api/location HTTP/1.1
	Host: client.com 
	Accept: application/json

with payload:

.. code-block:: json
	
	{
	"data": {
		"attributes": {
			"title": "Iqbal Town",
			"latitude": 72.8176,
			"parent_id": -1,
			"longitude": 79.2998
			},
		"_embedded": {
			"city": {
				"data":{
					"title": "Multan",
					"latitude": 72.997,
					"longitude": 78.1234
					}
				}
			}
		}
	}

.. code-block:: http

	HTTP/1.1 201 CREATED
	Content-Type: application/json

	{
	"data": {
	"_embedded": {
		"city": {
			"data": {
			"id": 1,
			"attributes": {
				"title": "Multan",
				"latitude": 72.997,
				"longitude": 78.1234,
				"created_at": "2017-03-11T15:15:36.934432",
				"updated_at": "None"
			},
			"_link": "http://localhost:5000/api/city/1"
			},
			"meta": {
			"_type": "to_one",
			"_links": {
			"self": "http://localhost:5000/api/location/1/city/1"
			}
			}
		}
		},
		"id": 1,
		"attributes": {
			"title": "Iqbal Town",
			"latitude": 72.8176,
			"updated_at": "None",
			"parent_id": -1,
			"created_at": "2017-03-11T15:15:36.934432",
			"longitude": 79.2998
		},
		"_link": "http://localhost:5000/api/location/1"
	},
	"meta": {
		"message": "Created",
		"status_code": 201
	}
	}


