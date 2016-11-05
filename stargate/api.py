from flask import Blueprint, jsonify, request
from functools import wraps
from .models import Event
from .schemas import event_schema, events_schema
from .route_handler import Api, Resource
from .extentions import db

api_blueprint = Blueprint('api_blueprint', __name__)


api = Api(api_blueprint)


@api.route('/v1/events', 'event_id')
class EventResource(Resource):

    def get(self, event_id):

        if event_id is None:
            events = Event.query.all()
            return jsonify({"message" : "Request Successfull", "code": 200, "data": events_schema.dump(events).data})
        else:
            event = Event.query.get(event_id)
            if event is None:
                return jsonify({"message": "Resource Not Found", "code": 404})
            else:
                event_result = event_schema.dump(event)
                return jsonify({"message" : "Request Successfull", "code": 200,'data': event_result.data})
    
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
