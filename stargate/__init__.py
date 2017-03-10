"""
.. note:: This project is currently under development. First version will soon be released.
		Currently flask-stargate has only test for GET and POST endpoints. More tests and features
		will be added soon.

Stargate is a framework for exposing RESTFul JSON APIs using Flask and Flask-SQLAlchemy. 
Currently it provides GET, POST, PATCH, DELETE endpoints against resources, pagination, filters, sorting,
grouping, resource expansion and partial responses. 

"""
from .manager import Manager
