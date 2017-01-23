from flask import Response

class ResponseCls(Response):
	charset = 'utf-8'
	default_mimetype = 'application/json'

	def __init__(self, response=None, **kwargs):
		return super(ResponseCls, self).__init__(response, **kwargs)

	@classmethod
	def force_type(cls, response, environ=None):
		return super(ResponseCls, cls).force_type(response, environ)