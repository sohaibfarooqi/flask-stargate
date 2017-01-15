from .stargate import create_app
from .config import ApplicationConfig
from functools import wraps
from flask import g, Flask
# from .stargate.entity_manager.models import db
from flask_sqlalchemy import SQLAlchemy
from .stargate.entity_manager.models import ServerLog, User, Location, City
from .stargate.entity_manager.exceptions import ApplicationError
from flask.ext.restless import APIManager

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
db = SQLAlchemy()
db.init_app(app)
manager = APIManager(app, flask_sqlalchemy_db = db)
manager.create_api(User, methods = ['GET', 'POST', 'DELETE'])
manager.create_api(Location, methods = ['GET', 'POST', 'DELETE'])
manager.create_api(City, methods = ['GET', 'POST', 'DELETE'])

manager.init_app(app)
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

	