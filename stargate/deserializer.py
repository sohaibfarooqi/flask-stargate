"""Default Deserialization Class for Stargate. It can convert JSONObject or JSONArray representation
of a resource to respective class object or list of objects.

"""

from .proxy import manager_info
from .utils import get_related_model
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from .utils import has_field, string_to_datetime, session_query
from .const import SerializationConst, ResourceInfoConst
from .exception import DeserializationException, UnknownRelation, MissingDataException
class Deserializer:
    
    def __init__(self, model, session):
        self.model = model
        self.session = session

    def __call__(self, document):
        
        if SerializationConst.DATA not in document:
            raise ValueError("Key Error data")
        
        data = document[SerializationConst.DATA]
        
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
            
            except DeserializationException as exception:
                raise DeserializationException(instance, str(exception))
        
        return result

    def _deserialize_one(self, instance):
        
        for field in instance:
            
            if field == SerializationConst._EMBEDDED:
                for relation in instance[SerializationConst._EMBEDDED]:
                    if not has_field(self.model, relation):
                        raise UnknownRelation(relation, self.model)
            
            elif field == SerializationConst.ATTRIBUTES:
                for attribute in instance[SerializationConst.ATTRIBUTES]:
                    if not has_field(self.model, attribute):
                        raise UnknownField(attribute, self.model)
        links = {}
        links = instance.pop(SerializationConst._EMBEDDED, {})
        related_resources = {}

        for rel_name, rel_object in links.items():

            if SerializationConst.DATA in rel_object:
                related_model = get_related_model(self.model, rel_name)
                deserialize = RelDeserializer(self.session, related_model, rel_name)
                related_resources[rel_name] = deserialize(rel_object[SerializationConst.DATA])
            else:
                raise MissingDataException(rel_name)
        
        data = instance.pop(SerializationConst.ATTRIBUTES, {})
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
            pk_name = manager_info(ResourceInfoConst.PRIMARY_KEY_FOR, self.model)
            
            if pk_name in data:
                return get_resource(self.session, self.model, data[pk_name])
            
            else:
                return self.model(**data)
        else:
            return list(map(self, data))