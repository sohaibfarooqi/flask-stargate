# from .stargate import create_app
from .config import ApplicationConfig
from functools import wraps
from flask import g, Flask
# from .stargate.entity_manager.models import db
from flask_sqlalchemy import SQLAlchemy
from .stargate.entity_manager.models import ServerLog, User, Location, City
from .stargate.entity_manager.exceptions import ApplicationError
from .stargate.core_api_v3 import ResourceManager

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
db = SQLAlchemy()
db.init_app(app)
manager = ResourceManager(app, flask_sqlalchemy_db = db)
manager.register_resource(User, methods = ['GET', 'POST', 'DELETE'])
manager.register_resource(Location, methods = ['GET', 'POST', 'DELETE'])
manager.register_resource(City, methods = ['GET', 'POST', 'DELETE'])
# @app.errorhandler(ApplicationError)
# def application_error(error):
# 	return error.message, 500

# @app.after_request
# def log_response(response):
	
# 	# log_object = ServerLog.query.filter(ServerLog.id == g.log_id).first()
# 	# log_object.response = str(response.response)
# 	# db.session.add(log_object)
# 	# db.session.commit()
	
# 	return response

# # @app.before_request
# # def authorize(request):
# # 	# for all application request common tasks

# if __name__ == '__main__':
app.run()

	