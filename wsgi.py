from .stargate import create_app
from .config import ApplicationConfig
from functools import wraps
from flask import g
from .stargate.extentions import db
from .stargate.entity_manager.models import ServerLog
from .stargate.entity_manager.exceptions import ApplicationError
from .stargate.middleware import ArgsParseMiddleware 

app = create_app(ApplicationConfig)
app.wsgi_app = ArgsParseMiddleware(app.wsgi_app)

@app.errorhandler(ApplicationError)
def application_error(error):
	return error.message, 500

@app.after_request
def log_response(response):
	
	# log_object = ServerLog.query.filter(ServerLog.id == g.log_id).first()
	# log_object.response = str(response.response)
	# db.session.add(log_object)
	# db.session.commit()
	
	return response

# @app.before_request
# def authorize(request):
# 	# for all application request common tasks

if __name__ == '__main__':
	app.run()

	