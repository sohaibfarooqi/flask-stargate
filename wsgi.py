from .models import User, Location, City
from .stargate import ResourceManager
from .app import init_app, init_db

app = init_app()
db = init_db(app)

manager = ResourceManager(app, flask_sqlalchemy_db = db)
manager.register_resource(User, methods = ['GET', 'POST', 'DELETE'])
manager.register_resource(Location, methods = ['GET', 'POST', 'DELETE'])
manager.register_resource(City, methods = ['GET', 'POST', 'DELETE'])

if __name__ == 'main':
	app.run()

	