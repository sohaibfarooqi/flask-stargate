from .config import ApplicationConfig
from flask import g, Flask
from flask_sqlalchemy import SQLAlchemy
from .models import User, Location, City
from .stargate.core_api import ResourceManager
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
db = SQLAlchemy()
db.init_app(app)
Migrate(app, db)
manager = ResourceManager(app, flask_sqlalchemy_db = db)

manager.register_resource(User, methods = ['GET', 'POST', 'DELETE'])
manager.register_resource(Location, methods = ['GET', 'POST', 'DELETE'])
manager.register_resource(City, methods = ['GET', 'POST', 'DELETE'])

app.run()

	