"""Default Deserialization Class for Stargate. It can convert JSONObject or JSONArray representation
of a resource to respective class object or list of objects."""

from .proxy import manager_info, PRIMARY_KEY_FOR
from .utils import get_related_model
from .query_helper.filter import string_to_datetime
from .query_helper.search import session_query
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from .utils import has_field

class Deserializer:
    
    def __init__(self, model, session):
        self.model = model
        self.session = session

    def __call__(self, document):
        
        if 'data' not in document:
            raise ValueError("Key Error data")
        
        data = document['data']
        
        if isinstance(data, list):
            return self._deserialize_many(data)
        
        else:
            return self._deserialize_one(data)

    def _deserialize_many(self, data):
        
        result = []
        for instance in data:
            try:
                deserialized = self._deserialize_one(instance)
                result.append(deserialized)
            
            except deserializationException as exception:
                raise DeserializationException(instance,str(exception))
        
        return result

    def _deserialize_one(self, instance):
        
        for field in instance:
            
            if field == '_embedded':
                for relation in instance['_embedded']:
                    if not has_field(self.model, relation):
                        raise ValueError("No relation found {0}".format(relation))
            
            elif field == 'attributes':
                for attribute in instance['attributes']:
                    if not has_field(self.model, attribute):
                        raise ValueError("No attribute found {0} for model {1}".format(relation, self.model))
        links = {}
        links = instance.pop('_embedded', {})
        related_resources = {}

        for rel_name, rel_object in links.items():

            if 'data' in rel_object:
                related_model = get_related_model(self.model, rel_name)
                deserialize = RelDeserializer(self.session, related_model, rel_name)
                related_resources[rel_name] = deserialize(rel_object['data'])
            else:
                raise KeyError("Missing data in relation {0}".format(rel_name))
        
        data = instance.pop('attributes', {})
        data = dict((k, string_to_datetime(self.model, k, v)) for k, v in data.items())
        
        instance = self.model(**data)
        
        for relation_name, related_value in related_resources.items():
            setattr(instance, relation_name, related_value)
        return instance

class RelDeserializer(Deserializer):

    def __init__(self, session, model, relation_name = None):

        super(RelDeserializer, self).__init__(model, session)
        self.relation_name = relation_name
    
    def __call__(self, data):

        if not isinstance(data, list):
            if 'id' in data:
                id_ = data['id']
                pk_name = manager_info(PRIMARY_KEY_FOR, self.model)
                query = session_query(self.session, self.model)
                query = query.filter(getattr(self.model, pk_name) == id_)
                try:
                    return query.one()
                except MultipleResultsFound as ex:
                    raise RuntimeError("Multiple `{0}` resources found against `id` {1}".format(self.relation_name, id_))
                except NoResultFound as ex:
                    raise RuntimeError("No Result Found for related Model `{0}` against `id` {1}".format(self.relation_name, id_))
            
            else:
                return self.model(**data)
        else:
            return list(map(self, data))