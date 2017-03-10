Dev Guide
=========

Description of Stargate classes/modules/functions.

.. module:: stargate.manager

The Manager Class
-----------------

.. autoclass:: Manager
	:members: __init__, register_resource, create_resource_blueprint

.. module:: stargate.resource_api

Resource API View
-----------------

.. autoclass:: ResourceAPI
	:members: get, post, patch, delete

.. module:: stargate.serializer

Serialization
-----------------

.. autoclass:: Serializer
	:members: __call__, _serialize_many, _serialize_one

.. module:: stargate.deserializer

Deserialization
-----------------

.. autoclass:: Deserializer
	:members: __call__, _deserialize

.. module:: stargate.resource_info

Global Helper
-----------------

.. autoclass:: ResourceInfo