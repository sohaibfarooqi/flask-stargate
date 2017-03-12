from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate
from .config import ApplicationConfig

#Flask-Sqlalchemy Instance.
db = SQLAlchemy()

def configure_db_extention(app):
	#Initilize db with Flask application instance.
	db.init_app(app)
	#Migration setup.							
	Migrate(app, db)

def init_app(test=False):
	#Init Flask
	app = Flask(__name__)
	#Apply configurations.
	app.config.from_object(ApplicationConfig)
	#If tests are to be executed.
	if test:
		app.config['TESTING'] = True
	#Invoke above function to configure database extention
	configure_db_extention(app)
	return app