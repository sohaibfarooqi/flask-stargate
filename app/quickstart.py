from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy import func
from ..stargate import Manager

#Create Flask application
app = Flask(__name__)
#Provide DB Connection String
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///test_db'
#Initilize db
db = SQLAlchemy()
db.init_app(app)
Migrate(app, db)

#Model Definition
class User(db.Model,Entity,TimestampMixin):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
	name = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)

#Resource Manager creation
manager = Manager(app, db)
#Registering `User` model with `manager` instance.
manager.register_resource(User, methods = ['GET'])

#Run flask app
app.run()