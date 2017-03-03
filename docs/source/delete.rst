======
DELETE
======

Delete method can be used to delete a resource with a specific primary key id

Delete Resource
----------------

Resource `User`:

.. sourcecode:: http

	DELETE /api/user/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

will yield a response:

.. sourcecode:: http
	
   	HTTP/1.1 204 No Content
   	
Delete Related Resource
-----------------------

Resource `User`:

.. sourcecode:: http

	DELETE /api/user/1/images/1 HTTP/1.1
	Host: client.com 
	Accept: application/json

will yield a response:

.. sourcecode:: http
	
   	HTTP/1.1 204 No Content
