from .app.models import User, Location, City
from .stargate import Manager
from .app import init_app, db

#Initilize `Flask Application`
app = init_app()

#Initilize `Manager` Instance
manager = Manager(app, db)
#Register Model with manager.
manager.register_resource(User, methods = ['GET', 'POST', 'PATCH', 'DELETE'])
manager.register_resource(Location, methods = ['GET', 'POST', 'PATCH','DELETE'])
manager.register_resource(City, methods = ['GET', 'POST', 'PATCH', 'DELETE'])

#Run the application
#This can be invoked from terminal as:
# >>flask run
if __name__ == 'main':
	app.run()

	