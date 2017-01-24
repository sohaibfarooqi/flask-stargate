
class CollectionRepresentation:
	def __init__(self, *args, **kwargs):
		self._links = {}
		self._link_header = {}
        self._num_results = 1
        self._data = []
        self._included = []
        self._single = False

	@property
	def links(self):
		return self._links

	@property
	def link_header(self):
		return self._link_header

	@property
	def num_results(self):
		return self._num_results

	@property
	def included(self):
		return self._included

	@property
	def data(self):
		return self._inclusions
