from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from ..config import ApplicationConfig
from flask_migrate import Migrate

def init_db(app):
	db = SQLAlchemy()
	db.init_app(app)
	Migrate(app, db)
	return db

def init_app():
	app = Flask(__name__)
	app.config.from_object(ApplicationConfig)
	return app