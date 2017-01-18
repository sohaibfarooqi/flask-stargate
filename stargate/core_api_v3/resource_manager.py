class ResourceManager(object):
	"""Class to manage db Entities. 
	"""
	
	def __init__(self, app=None, session=None, flask_sqlalchemy_db=None,
                 preprocessors=None, postprocessors=None, url_prefix=None):
	"""Class Constructor"""
