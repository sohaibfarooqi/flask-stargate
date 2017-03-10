Guidelines on creating API Endpoints
====================================

To use this project you first need to define all your models and relationships using using 
`Flasks'` extention ``Flask-Sqlalchemy``. Check out docs : `flask_sqlahcemy_docs`_.

Lets consider the example in quickstart again. I am going to skip model definition, Flask and Flask-Sqlalchemy initilization

.. sourcecode:: python

	from stargate import ResourceManager
	from models import User

	manager = ResourceManager(app, db = db)
	manager.register_resource(User, methods = ['GET'])

First line initilize ``ResourceManager`` instance, which requires ``Flask`` app and 
``SqlAlchemy`` instance

Second line exposes HTTP GET method for ``User`` model. If you are running this at your 
localhost you can excess this resource at: 
``http://localhost:5000/api/user``.
By default the resource endpoint will be ``Resource.__tablename__``.


Customizing API Endpoints
-------------------------
API Endpoints supports following customizations:

Url Prefix
++++++++++

.. code-block:: python

	manager = ResourceManager(app, db = db, url_prefix = '/v1')

Specifying url_prefix only for a resource

.. code-block:: python

	manager.register_resource(User, url_prefix = '/adminusers')

Http Methods
++++++++++++

.. code-block:: python

	manager.register_resource(User, methods = ['GET'], methods = ['GET', 'POST'])

Any other Http method will result in 405 (MethodNotAllowed)

Custom endpoint
+++++++++++++++
.. code-block:: python

	manager.register_resource(User, methods = ['GET'], endpoint = 'my_custom_collection')

Now on localhost ``User`` resource is accessible at: http://localhost:5000/api/my_custom_collection

Limiting Resource attributes
++++++++++++++++++++++++++++

.. code-block:: python

	manager.register_resource(User, fields = ['name', 'username'])

Now GET request on ``/user`` will only result in ``name`` and ``username`` keys. Primary key will always be included in response. 

Exclude Some Attributes
+++++++++++++++++++++++

.. code-block:: python

	manager.register_resource(User, exclude = ['name', 'username'])

The response will result in all attributes of ``User`` except ``name`` and ``username``.

Related Resources	
+++++++++++++++++

.. code-block:: python

	manager.register_resource(User, expand = ['city', 'location'])

By default all embedded resources will only have link and relationship type in it. expand option
will expand the specified resources.

View Decorators
+++++++++++++++

.. code-block:: python

	from my_decorators import decorator
	manager.register_resource(User, decorators = [decorator])

Specify Primary Key
++++++++++++++++++++

.. code-block:: python

	manager.register_resource(User, primary_key = 'ser_id')

Now in all over application primary key column used will be ``ser_id``

.. _flask_sqlahcemy_docs: http://flask-sqlalchemy.pocoo.org/2.1/