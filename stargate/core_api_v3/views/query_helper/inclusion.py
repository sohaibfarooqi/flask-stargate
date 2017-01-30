from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import RelationshipProperty as RelProperty
from sqlalchemy.ext.associationproxy import AssociationProxy

NON_RELATION_ATTRS = ('query', 'query_class', '_sa_class_manager','_decl_class_registry')

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