"""Application Constants. Import in different modules and test cases"""

class PaginationConst:
	PAGE_NUMBER = 1
	PAGE_SIZE = 10
	MAX_PAGE_SIZE = 100

class QueryStringConst:
	FILTER = 'filters'
	SORT = 'sort'
	GROUP = 'group'
	FIELDS = 'field'
	EXPAND = 'expand'
	EXCLUDE = 'exclude'
	PAGE_SIZE = 'page_size'
	PAGE_NUMBER = 'page_number'

class ResourceConst:
	PRIMARY_KEY_COLUMN = 'id'

class RelTypeConst:
	TO_MANY = 'to_many'
	TO_ONE = 'to_one'

class CollectionEvaluationConst:
	EAGER = 'eager'
	LAZY = 'lazy'

class SerializationConst:
	_EMBEDDED = '_embedded'
	ATTRIBUTES = 'attributes'
	DATA = 'data'
	NUM_RESULTS = 'num_results'
	LINKS = 'links'

class ResourceInfoConst:
	PRIMARY_KEY_FOR = 'primary_key_for'
	SERIALIZER_FOR = 'serializer_for'
	DESERIALIZER_FOR = 'deserializer_for'
	URL_FOR = 'url_for'
	COLLECTION_NAME_FOR = 'collection_name_for'