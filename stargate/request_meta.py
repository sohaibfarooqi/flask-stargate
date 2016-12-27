
class RequestMeta():
	
	def __init__(self, environ):
		
		self.lang, self.api_version, self.content_type, self.media_type, self.x_auth_key = self._parse(environ)


	def _parse(self, environ):
		
		lang = environ.get('Accept_Language', None)
		request_parser_class = Negotiation.get_parser(environ.get('QUERY_STRING'), environ.get('Content-Type', None))
		response_renderer_class = Negotiation.get_renderer(renviron.get('Accept', None))
		x_auth_key = environ.get('X_AUTH_KEY', None)
		content_length = environ.get('Content-Length', None)

		return lang,request_parser_class,response_renderer_class,x_auth_key 



