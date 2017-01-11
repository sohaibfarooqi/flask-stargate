from flask import Blueprint, jsonify, request,g
from functools import wraps
from .entity_manager.models import Event, User, ServerLog, Entity
from .entity_manager import EntityManager
from .schemas import event_schema, events_schema, user_schema, users_schema
from .route_handler import Api, Resource
from .auth import Authorization

api_blueprint = Blueprint('api_blueprint', __name__)
api = Api(api_blueprint)

__custom_endpoints__ = ('login', 'signup')

@api_blueprint.before_request
def authorize():

    #Log Request Data
    # server_log = ServerLog()
    # server_log.headers = request.headers.__repr__()
    # server_log.request_method = request.environ['REQUEST_METHOD']
    # request_data = request.get_json(silent= True)
    # server_log.body_part = str(request_data)
    # server_log.request_url = request.url
    # db.session.add(server_log)
    # db.session.commit()
    # g.log_id = server_log.id
    
    #Authorize Request
    endpoint = request.endpoint.split('.')
    
    # if endpoint[1] in __custom_endpoints__:
    #    pass
    
    # elif Authorization.authorize_request(request.headers):
    #     pass
    
    # else:
    #     return jsonify({"code":401, "message:":"Unauthorized Request"})
    

@api.route('/v1/users', 'user_id')
class UserResource(Resource):
    
    def get(self, user_id):

        users = EntityManager.get(User, user_id, request.args)
        return jsonify({"message" : "Request Successful", "code": 200,'data': users_schema.dump(users).data})
        
    def post(self):
        try:
            users = user_schema.load(request.get_json(silent=False)).data
            db.session.add(users)
            db.session.commit()
            return jsonify({"message": "Resource Created", "code": 201, "data": user_schema.dump(users).data})
        except ValueError as err:
            return jsonify({"message": "Bad Request", "code": 400, "error-details":err.args})

    def put(self, user_id):
        
        if user_id is None:
            return jsonify({"message": "Bad Request", "code": 400})
        
        else:
            return jsonify({"message": "Resource Updated", "code": 201, "data": Entity.update_one(User,user_id,request.get_json(silent=False))})

    def delete(self, user_id):
        
        if user_id is None:
            return jsonify({"message": "Bad Request", "code": 400})
        
        else:
            existing_user = User.query.filter(User.id == user_id).delete()
            db.session.commit()
            return jsonify({"message": "Deleted Successfully", "code": 201})