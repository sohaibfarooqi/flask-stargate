from .app.models import User, Location, City
from .stargate import Manager
from .app import init_app, db

app = init_app()

manager = Manager(app, db)
manager.register_resource(User, methods = ['GET', 'POST', 'PATCH', 'DELETE'])
manager.register_resource(Location, methods = ['GET', 'POST', 'PATCH','DELETE'])
manager.register_resource(City, methods = ['GET', 'POST', 'PATCH', 'DELETE'])

if __name__ == 'main':
	app.run()

	