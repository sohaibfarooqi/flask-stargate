from .config import ApplicationConfig
from flask import g, Flask
from flask_sqlalchemy import SQLAlchemy
from .models import User, Location, City
from .stargate.core_api import ResourceManager
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

app = init_app()
db = init_db(app)

manager = ResourceManager(app, flask_sqlalchemy_db = db)
manager.register_resource(User, methods = ['GET', 'POST', 'DELETE'])
manager.register_resource(Location, methods = ['GET', 'POST', 'DELETE'])
manager.register_resource(City, methods = ['GET', 'POST', 'DELETE'])

if __name__ == 'main'
	app.run()

	