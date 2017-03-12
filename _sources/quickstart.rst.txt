Quickstart
=============
 
You can also view this example online. ``wsgi.py`` is in root: `wsgi`_, while
helpers(Models, App setup) resides in app directory : `app`_.

Main Application Code
---------------------
.. literalinclude:: ../../wsgi.py
	:linenos:

Model Classes
-------------
Register your models with ``Flask-Sqlalchemy``

.. literalinclude:: ../../app/models.py
	:linenos:

Application Setup
-----------------
Configure db extention and migrations. Initilize `Flask` application.

.. literalinclude:: ../../app/__init__.py
	:linenos:

.. _wsgi: https://github.com/sohaibfarooqi/stargate/blob/master/wsgi.py
.. _app: https://github.com/sohaibfarooqi/stargate/blob/master/app