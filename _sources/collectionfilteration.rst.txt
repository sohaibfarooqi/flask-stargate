=====================
Filtering Collections
=====================

Collection filteration is supported in following format

Filters
--------
Following example shows a basic use of resource filteration

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

Pagination
-----------
Pagination on collections can be simply performed as follows:

.. sourcecode:: http

	GET /api/user?page=1&perpage=20 HTTP/1.1
	Host: client.com 
	Accept: application/json

This will result in 20 ``User`` objects starting from first. By default ``page=1``
and ``perpage=10``. ``perpage`` cannot go beyond 100.

Partial Response
-----------------
Partial response can be done in two ways:
 
	1. Selective attributes

	.. sourcecode:: http

		GET /api/user?fields=name,age HTTP/1.1
		Host: client.com 
		Accept: application/json

		This response objects will only contain `name` and `age` keys.

	2. Excluding attributes

	.. sourcecode:: http

		GET /api/user?exclude=name,age HTTP/1.1
		Host: client.com 
		Accept: application/json

		This response objects will contain all attributes except`name` and `age`.


Resource Expansion
------------------
Related resources can be expanded in a following manner:

.. sourcecode:: http

	GET /api/user?expand=location HTTP/1.1
	Host: client.com 
	Accept: application/json

By default related resource will only have link in their data, which can be used
to get the resource.

You can also specify selective fields on related resources

.. sourcecode:: http

	GET /api/user?expand=location(latitude,longitude) HTTP/1.1
	Host: client.com 
	Accept: application/json

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
