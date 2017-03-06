"""Application Constants that are used in more than one module or in test cases.

"""
#Pagination Constants
class PaginationConst:
	PAGE_NUMBER = 1
	PAGE_SIZE = 10
	MAX_PAGE_SIZE = 100

#Request Query String Constants
class QueryStringConst:
	FILTER = 'filters'
	SORT = 'sort'
	GROUP = 'group'
	FIELDS = 'field'
	EXPAND = 'expand'
	EXCLUDE = 'exclude'
	PAGE_SIZE = 'page_size'
	PAGE_NUMBER = 'page_number'

#Resource Constants
class ResourceConst:
	PRIMARY_KEY_COLUMN = 'id'

#Relationship Type Constants
class RelTypeConst:
	TO_MANY = 'to_many'
	TO_ONE = 'to_one'

#Collection Evaluation Constants
class CollectionEvaluationConst:
	EAGER = 'eager'
	LAZY = 'lazy'

#Serialization Constants
class SerializationConst:
	EMBEDDED = '_embedded'
	ATTRIBUTES = 'attributes'
	DATA = 'data'
	NUM_RESULTS = 'num_results'
	LINKS = 'links'

#Resource Info Constants
class ResourceInfoConst:
	PRIMARY_KEY = 'primary_key_for'
	SERIALIZER = 'serializer_for'
	DESERIALIZER = 'deserializer_for'
	URL = 'url_for'
	COLLECTION_NAME = 'collection_name_for'

class MediatypeConstants:
	CONTENT_TYPE = 'application/json'
	import re
	ACCEPT_RE = re.compile(
	    r'''(                       # media-range capturing-parenthesis
	          [^\s;,]+              # type/subtype
	          (?:[ \t]*;[ \t]*      # ";"
	            (?:                 # parameter non-capturing-parenthesis
	              [^\s;,q][^\s;,]*  # token that doesn't start with "q"
	            |                   # or
	              q[^\s;,=][^\s;,]* # token that is more than just "q"
	            )
	          )*                    # zero or more parameters
	        )                       # end of media-range
	        (?:[ \t]*;[ \t]*q=      # weight is a "q" parameter
	          (\d*(?:\.\d+)?)       # qvalue capturing-parentheses
	          [^,]*                 # "extension" accept params: who cares?
	        )?                      # accept params are optional
	    ''', re.VERBOSE)