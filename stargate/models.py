from .extentions import db
from sqlalchemy import func

class Entity:
    id = db.Column(db.Integer, primary_key=True)

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

class Package(db.Model,Entity,TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.String)
    
    def __init__(self, id, title, description, price):
        self.id = id
        self.title = title
        self.description = description
        self.price = price
        
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)
    address = db.Column(db.String)
    description = db.Column(db.String)
    logo_url = db.Column(db.String)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    package = db.relationship('Package', backref = db.backref('organization', lazy='dynamic'))

    def __init__(self, id, name, phone, email, address, city_id, description, package_id, logo_url):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.city_id = city_id
        self.description = description
        self.package_id = package_id
        self.logo_url = logo_url
