from flask import Blueprint, request, Request
from functools import wraps
from .route_handler import RouteHanlder


"""
Entry point of all requests.
"""

api_blueprint = Blueprint('api_blueprint', __name__)
api = RouteHanlder(api_blueprint)

@api.route('/<script_path>', 'parent_id')
def process_request (script_path, parent_id = -1):
	pass