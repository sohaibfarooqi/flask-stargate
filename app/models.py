import datetime
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
import sqlalchemy.orm
from . import db

class Entity:
    
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    def __init__(self, **kwargs):
         
         self.__dict__.update(kwargs)
         
         for key in kwargs:
            self.key = kwargs[key]

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    
class Location(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    parent_id = db.Column(db.Integer)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    city = db.relationship('City')

class City(db.Model,Entity,TimestampMixin):
    title = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location = db.relationship('Location')    
    user = db.relationship('User', lazy = 'dynamic')    

class User(db.Model,Entity,TimestampMixin):
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String)
    pic_url = db.Column(db.String)
    age = db.Column(db.Integer)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    city = db.relationship('City', cascade="all")
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location = db.relationship('Location', cascade="all")

class TestPrimaryKey(db.Model):
    ser_id = db.Column(db.Integer, primary_key = True, autoincrement = True)    

