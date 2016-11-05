from marshmallow import Schema, post_load, fields
from .models import Event
class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    start_date = fields.Date()
    end_date = fields.Date()
    address = fields.Str()
    guests = fields.Str()
    images = fields.Str()
    videos = fields.Str()
    city_id = fields.Int()
    location_id = fields.Int()
    event_type_id = fields.Int()
    created_at = fields.Date()
    updated_at = fields.Date()

    @post_load
    def make_event(self, data):
        return Event(**data)

event_schema = EventSchema()
events_schema = EventSchema(many=True)

