from .extentions import db
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
import datetime

class Entity:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

class Package(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.String)
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        for key in kwargs:
            self.key = kwargs[key]

class Location(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    parent_id = db.Column(db.Integer)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City', backref = db.backref('location', lazy='dynamic'))
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        for key in kwargs:
            self.key = kwargs[key]

class City(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        for key in kwargs:
            self.key = kwargs[key]

class Organization(db.Model,Entity,TimestampMixin):
    name = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)
    address = db.Column(db.String)
    description = db.Column(db.String)
    logo_url = db.Column(db.String)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    package = db.relationship('Package', backref = db.backref('organization', lazy='dynamic'))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City', backref = db.backref('organization', lazy='dynamic'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', backref = db.backref('organization', lazy='dynamic'))
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        for key in kwargs:
            self.key = kwargs[key]
        
class Event(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    address = db.Column(db.String)
    guests = db.Column(db.String)
    images = db.Column(db.String)
    videos = db.Column(db.String)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City', backref = db.backref('event', lazy='dynamic'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', backref = db.backref('event', lazy='dynamic'))
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_type.id'))
    event_type = db.relationship('EventType', backref = db.backref('event', lazy='dynamic'))
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        for key in kwargs:
            self.key = kwargs[key]

    def __iter__(self):
        yield 

class EventType(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        for key in kwargs:
            self.key = kwargs[key]

class EventComment(db.Model,Entity,TimestampMixin):
    message = db.Column(db.String)
    user_id = db.Column(db.Integer)
    path = db.Column(db.String)
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        for key in kwargs:
            self.key = kwargs[key]

class User(db.Model,Entity,TimestampMixin):
    name = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    pic_url = db.Column(db.String)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City', backref = db.backref('user', lazy='dynamic'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', backref = db.backref('user', lazy='dynamic'))
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        for key in kwargs:
            self.key = kwargs[key]

class Auth(db.Model,Entity,TimestampMixin):
    auth_token = db.Column(db.String)
    expires_at = db.Column(db.DateTime)
    ip_address = db.Column(db.String)
    user_agent = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref = db.backref('auth', lazy='dynamic'))
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        for key in kwargs:
            self.key = kwargs[key]

    @hybrid_property
    def remaining_time(self):
        return (self.expires_at - datetime.datetime.now()).seconds  // 60 % 60