from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import RelationshipProperty as RelProperty
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.inspection import inspect
import re

NON_RELATION_ATTRS = ('query', 'query_class', '_sa_class_manager','_decl_class_registry')

REGEX_MATCH_FIELD = r'((\w+)\(([\s+\w\s+,\s+.]+)\))'

class Inclusions():
	
	def get_relations(model):
		return [k for k in dir(model) if not (k.startswith('__') or k in NON_RELATION_ATTRS) and Inclusions.get_related_model(model, k)]
	
	def get_related_model(model, relationname):
		
		if hasattr(model, relationname):
			attr = getattr(model, relationname)
			if hasattr(attr, 'property') and isinstance(attr.property, RelProperty):
				return attr.property.mapper.class_
			if isinstance(attr, AssociationProxy):
				return Inclusions.get_related_association_proxy_model(attr)
		return None

	def get_related_association_proxy_model(attr):
		prop = attr.remote_attr.property
		for attribute in ('mapper', 'parent'):
			if hasattr(prop, attribute):
				return getattr(prop, attribute).class_
		return None       


	def parse_expansions(model, expand):
		
		nested_fields = re.findall(REGEX_MATCH_FIELD, expand)

		resource = expand
		resource = re.sub(REGEX_MATCH_FIELD, '', resource)
		resource = re.sub(r'\s+', '', resource)
		resource = re.sub(r'\A(?:\s+)?,(?:\s+)?', '', resource)
		resource = re.sub(r'(?:\s+)?,(?:\s+)?$', '', resource)
		resource = resource.split(',')
		expand_full = set(resource)
		
		all_relations = Inclusions.get_relations(model)
		all_joins = set()
		expand_partial = list()
		for fields in nested_fields:
			if fields[1] in all_relations:
				nested_resource_fields = [field.strip() for field in fields[2].split(',') if field is not None]
				resource_fields = set(nested_resource_fields)
				expand_partial.append((fields[1], resource_fields))
		return dict(expand_full=expand_full, expand_partial=expand_partial)
		