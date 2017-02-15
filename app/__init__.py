from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate
from .config import ApplicationConfig

db = SQLAlchemy()

def configure_db_extention(app):
	db.init_app(app)
	Migrate(app, db)

def init_app():
	app = Flask(__name__)
	app.config.from_object(ApplicationConfig)
	configure_db_extention(app)
	return app