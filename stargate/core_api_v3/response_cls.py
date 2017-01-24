from flask import Response
from .mimerender import MimeRender

class ResponseCls(Response):
	charset = 'utf-8'
	default_mimetype = 'application/json'

	def __init__(self, response=None, **kwargs):
		response = MimeRender.create_response()
		return super(ResponseCls, self).__init__(response, **kwargs)