import re
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import NoInspectionAvailable
from ...proxy import collection_name_for
from ...exception import IllegalArgumentError
from .inclusion import Inclusions

DEFAULT_FIELD_LIST = ['id', 'created_at', 'updated_at']
REGEX_MATCH_FIELD = r'((\w+)\(([\s+\w\s+,\s+.]+)\))'

class Fields():

	def get_effective_fields(model, include_fields):
		
		nested_fields = re.findall(REGEX_MATCH_FIELD, include_fields)

		resource_fields = include_fields
		resource_fields = re.sub(REGEX_MATCH_FIELD, '', resource_fields)
		resource_fields = re.sub(r'\s+', '', resource_fields)
		resource_fields = re.sub(r'\A(?:\s+)?,(?:\s+)?', '', resource_fields)
		resource_fields = re.sub(r'(?:\s+)?,(?:\s+)?$', '', resource_fields)
		resource_fields = resource_fields.split(',')
		resource_fields.extend(DEFAULT_FIELD_LIST)
		resource_fields = set(resource_fields)

		all_fields = [getattr(model, col) for col in resource_fields]
		all_relations = Inclusions.get_relations(model)
		all_joins = set()
		for fields in nested_fields:
			if fields[1] in all_relations:
				nested_resource_fields = [field.strip() for field in fields[2].split(',') if field is not None]
				nested_resource_fields.extend(DEFAULT_FIELD_LIST)
				nested_resource_fields = set(nested_resource_fields)
				relation_model = Inclusions.get_related_model(model, fields[1])
				all_joins.add(relation_model)
				all_fields.extend([getattr(relation_model, col) for col in nested_resource_fields])
		return all_fields,all_joins
	
	def get_effective_fields_1(model, include_fields, exclude_fields):
		
		fields = []
		all_relations = Inclusions.get_relations(model)
		all_columns = Fields._get_all_columns(model, all_relations)
		fields = [val for val in all_columns if val in include_fields or val in DEFAULT_FIELD_LIST]

		for inc_field in include_fields:
			relation_model = None
			if '.' in inc_field:
				field_name, field_name_in_relation = inc_field.split('.')
				relation_model = Inclusions.get_related_model(model, field_name)
				field = getattr(relation_model, field_name_in_relation)
			else:
				field = getattr(model, inc_field)
			fields.append((field, relation_model))
		return fields
    
	def _get_all_columns(model, relationlist):
		all_columns = []
		try:
			inspected_instance = inspect(model)
		except NoInspectionAvailable:
			msg = "No Inspection available for model {0}".format(collection_name_for(model))
			raise IllegalArgumentError(msg=msg)

		column_attrs = inspected_instance.column_attrs.keys()
		descriptors = inspected_instance.all_orm_descriptors.items()
		hybrid_columns = [k for k, d in descriptors if d.extension_type == HYBRID_PROPERTY]

		all_columns.extend(column_attrs)
		all_columns.extend(hybrid_columns)
		
		for relation in relationlist:
			relation = Inclusions.get_related_model(model, relation)
			try:
				inspected_instance = inspect(relation)
			except NoInspectionAvailable:
				msg = "No Inspection available for model {0}".format(collection_name_for(relation))
				raise IllegalArgumentError(msg=msg)
			
			column_attrs = inspected_instance.column_attrs.keys()
			descriptors = inspected_instance.all_orm_descriptors.items()
			hybrid_columns = [k for k, d in descriptors if d.extension_type == HYBRID_PROPERTY]
			
			column_attrs = ['{0}.{1}'.format(relation.__name__, val) for val in column_attrs]
			hybrid_columns = ['{0}.{1}'.format(relation.__name__, val) for val in hybrid_columns]
			all_columns.extend(column_attrs)
			all_columns.extend(hybrid_columns)
		return all_columns