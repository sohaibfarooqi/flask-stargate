import datetime
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
import sqlalchemy.orm

db = SQLAlchemy()

class Entity:
    
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    def __init__(self, **kwargs):
         
         self.__dict__.update(kwargs)
         
         for key in kwargs:
            self.key = kwargs[key]

    def get_collection(model, print_query, **kwargs):
        
        query = model.query
        offset, page_size = 0,10

        if 'fields' in kwargs and isinstance(kwargs['fields'], list) and len(kwargs['fields']) > 0:
            
            query = query.with_entities(*kwargs['fields'])

        if 'embed' in kwargs and isinstance(kwargs['embed'], list) and len(kwargs['embed']) > 0:
            
            query = query.outerjoin(*kwargs['embed'])
        
        if 'embed_inner' in kwargs and isinstance(kwargs['embed_inner'], list) and len(kwargs['embed_inner']) > 0:
            
            query = query.join(*kwargs['embed_inner'])            
        
        if 'filters' in kwargs and len(kwargs['filters']) > 0:
            
            if isinstance(kwargs['filters'], list):
                query = query.filter(*kwargs['filters'])
            else:    
                query = query.filter(kwargs['filters'])
        
        if 'sort_order' in kwargs and isinstance(kwargs['sort_order'], list) and len(kwargs['sort_order']) > 0:

            query = query.order_by(*kwargs['sort_order'])
        
        query = query.offset(offset).limit(page_size)
        
        # if print_query: 
            # print(Entity.query_str_repr(query))
        
        return  query.all()

    def get_one(model, pk_id, print_query, **kwargs):
        
        query = model.query

        if 'embed' in kwargs and isinstance(kwargs['embed'], list) and len(kwargs['embed']) > 0:
            
            query = query.outerjoin(*kwargs['embed'])
        
        if 'embed_inner' in kwargs and isinstance(kwargs['embed_inner'], list) and len(kwargs['embed_inner']) > 0:
            
            query = query.join(*kwargs['embed_inner'])

        query = query.filter(model.id == pk_id)
        
        # if print_query : 
            # print(Entity.query_str_repr(query))

        return query.first()

    def query_str_repr(query):
        if isinstance(query, sqlalchemy.orm.Query):
            return str(query.statement.compile( dialect=postgresql.dialect(), 
                                                compile_kwargs={"literal_binds": True}
                                                ))

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

class Package(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.String)
    
class Location(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    parent_id = db.Column(db.Integer)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City', backref = db.backref('location', lazy='dynamic'))
    
class City(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

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
    
class EventType(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    
class EventComment(db.Model,Entity,TimestampMixin):
    message = db.Column(db.String)
    user_id = db.Column(db.Integer)
    path = db.Column(db.String)
    
class User(db.Model,Entity,TimestampMixin):
    name = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    pic_url = db.Column(db.String)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    age = db.Column(db.Integer)
    city = db.relationship('City', backref = db.backref('user', lazy='dynamic'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', backref = db.backref('user', lazy='dynamic'))

class Auth(db.Model,Entity,TimestampMixin):
    auth_token = db.Column(db.String)
    expires_at = db.Column(db.DateTime)
    ip_address = db.Column(db.String)
    user_agent = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref = db.backref('auth', lazy='dynamic'))
    
    @hybrid_property
    def remaining_time(self):
        if self.expires_at > datetime.datetime.now():
            return (self.expires_at - datetime.datetime.now()).seconds  // 60 % 60
        else:
            return 0


class ServerLog(db.Model,Entity,TimestampMixin):
    headers = db.Column(db.String)
    body_part = db.Column(db.String)
    request_method = db.Column(db.String)
    request_url = db.Column(db.String)
    response = db.Column(db.String)
