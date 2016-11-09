from marshmallow import Schema, post_load, pre_load, post_dump, post_load, fields,validate,validates_schema, ValidationError
from .models import Event, User

class BaseSchema(Schema):
    id = fields.Int(dump_only = True, required = True)
    created_at = fields.Date(dump_to = "created")
    updated_at = fields.Date(dump_to = "updated")

    __envelope__ = {
        'single': None,
        'many': None
    }
    __model__ = User

    def get_envelope_key(self, many):
        key =  self.__envelope__['many'] if many else self.__envelope__['single']
        assert key is not None, "Envelope key undefined"
        return key

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many):
        key = self.get_envelope_key(many)
        return data[key]

    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many):
        key = self.get_envelope_key(many)
        return {key: data}

    @post_load
    def make_object(self, data):
        return self.__model__(**data)


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
    
class UserSchema(BaseSchema):
    __envelope__ = {
        'single': 'user',
        'many': 'users',
    }
    __model__ = User
    name = fields.Str(max_length = 80)
    username = fields.Str(unique = True, max_length = 50)
    password = fields.Str(load_only = True, validate = [validate.Length(min = 6,max = 12,error='Invalid Password Text')])
    email = fields.Email(required = True, unique=True, error = "Invalid Email Address", max_length = 100)
    phone = fields.Str(validate = [validate.Length(min = 10,max = 12,error='Invalid Phone Number')])
    pic_url = fields.Str(max_length = 50, validate = [validate.Regexp('[^\s]+(\.(?i)(jpg|png))$',error="Invalid Image File Name")])
    city_id = fields.Int()
    location_id = fields.Int()

# @validates_schema
# def validate_numbers(self, data):
#     if data['location_id'] > 10:
#         raise ValidationError('location_id must be less than 10')

@UserSchema.error_handler
def handle_errors(schema, errors, obj):
    raise ValueError(errors)



user_schema = UserSchema()
users_schema = UserSchema(many = True)