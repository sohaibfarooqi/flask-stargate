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
    
class Location(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    parent_id = db.Column(db.Integer)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City', backref = db.backref('city', lazy='dynamic'))    
    
class City(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location = db.relationship('Location', backref = db.backref('locationid'))    
        

    
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

# class Auth(db.Model,Entity,TimestampMixin):
#     auth_token = db.Column(db.String)
#     expires_at = db.Column(db.DateTime)
#     ip_address = db.Column(db.String)
#     user_agent = db.Column(db.String)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     user = db.relationship('User', backref = db.backref('auth', lazy='dynamic'))
    
#     @hybrid_property
#     def remaining_time(self):
#         if self.expires_at > datetime.datetime.now():
#             return (self.expires_at - datetime.datetime.now()).seconds  // 60 % 60
#         else:
#             return 0

