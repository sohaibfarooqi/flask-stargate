from .stargate import create_app
from .config import ApplicationConfig
from functools import wraps

app = create_app(ApplicationConfig)

@app.after_request
def log_response(response):
	print('WSGI.py')
	return response

# @app.before_request
# def authorize(request):
# 	# for all application request common tasks

if __name__ == '__main__':
	app.run()

	