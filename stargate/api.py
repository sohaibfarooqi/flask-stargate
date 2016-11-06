from flask import Blueprint, jsonify, request
from functools import wraps
from .models import Event, User
from .schemas import event_schema, events_schema, user_schema, users_schema
from .route_handler import Api, Resource
from .extentions import db
from .auth import Authorization


api_blueprint = Blueprint('api_blueprint', __name__)
api = Api(api_blueprint)

@api_blueprint.before_request
def authorize():
    if Authorization.authorize_request(request.headers):
        pass
    else:
        return jsonify({"code":401, "message:":"Unauthorized Request"})
    

@api.route('/v1/events', 'event_id')
class EventResource(Resource):

    def get(self, event_id):

        if event_id is None:
            events = Event.query.all()
            return jsonify({"message" : "Request Successful", "code": 200, "data": events_schema.dump(events).data})
        else:
            event = Event.query.get(event_id)
            if event is None:
                return jsonify({"message": "Resource Not Found", "code": 404})
            else:
                event_result = event_schema.dump(event)
                return jsonify({"message" : "Request Successful", "code": 200,'data': event_result.data})
    
    def post(self):
        events = event_schema.load(request.get_json(silent=False)).data
        db.session.add(events)
        db.session.commit()
        return jsonify({"message": "Resource Created", "code": 201, "data": event_schema.dump(events).data})
    
    def put(self, event_id):
        if event_id is None:
            return jsonify({"message": "Bad Request", "code": 400})
        else:
            existing_event = Event.query.filter_by(id=event_id).update(request.get_json(silent=False))
            db.session.commit()
            return jsonify({"message": "Resource Updated", "code": 201, "data": existing_event})

    def delete(self, event_id):
        if event_id is None:
            return jsonify({"message": "Bad Request", "code": 400})
        else:
            existing_event = Event.query.filter(Event.id == event_id).delete()
            db.session.commit()
            return jsonify({"message": "Deleted Successfully", "code": 201})

@api.route('/v1/users', 'user_id')
class UserResource(Resource):

    def get(self, user_id):

        if user_id is None:
            users = User.query.all()
            return jsonify({"message" : "Request Successful", "code": 200, "data": users_schema.dump(users).data})
        
        else:
            user = User.query.get(user_id)
            if user is None:
                return jsonify({"message": "Resource Not Found", "code": 404})
            else:
                return jsonify({"message" : "Request Successful", "code": 200,'data': user_schema.dump(user).data})
        
    def post(self):
        
        users = user_schema.load(request.get_json(silent=False)).data
        db.session.add(users)
        db.session.commit()
        return jsonify({"message": "Resource Created", "code": 201, "data": user_schema.dump(users).data})
    
    def put(self, user_id):
        
        if user_id is None:
            return jsonify({"message": "Bad Request", "code": 400})
        
        else:
            existing_user = User.query.filter_by(id=user_id).update(request.get_json(silent=False))
            db.session.commit()
            return jsonify({"message": "Resource Updated", "code": 201, "data": existing_user})

    def delete(self, user_id):
        
        if user_id is None:
            return jsonify({"message": "Bad Request", "code": 400})
        
        else:
            existing_user = User.query.filter(User.id == user_id).delete()
            db.session.commit()
            return jsonify({"message": "Deleted Successfully", "code": 201})