"""Default Deserialization Class for Stargate. It can convert JSONObject or JSONArray representation
of a resource to respective class object or list of objects.

"""

from .resource_info import resource_info
from .utils import get_related_model
from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from .utils import has_field, string_to_datetime, session_query
from .const import SerializationConst, ResourceInfoConst
from .exception import DeserializationException, UnknownRelation, MissingData

class Deserializer:
    """Default Deserializer class. Each resource regsiter its own copy of this class 
    during initilization in :class:`~stargate.manager.Manager`

    :param session: SQLALchemy session object.
    :param model: Resource model class.
    
    """
    def __init__(self, model, session):
        self.model = model
        self.session = session

    def __call__(self, document):
        """Callable for Deserializer class. Can deserialize JSONArray or JSONObject representation.
        Raise :class:`~stargate.exception.MissingDataKey` id `data` key is not present in request payload.

        Example:

        .. code-block:: python
        
            deserializer = resource_info(ResourceInfoConst.DESERIALIZER, User)
            #This execute callable.
            data = deserializer(data)

        :param document: JSON request payload.
        
        """
        if SerializationConst.DATA not in document:
            raise MissingDataKey("Key Error data")
        
        data = document[SerializationConst.DATA]
        
        if isinstance(data, list):
            return self._deserialize_many(data)
        
        else:
            return self._deserialize_one(data)

    def _deserialize_many(self, data):
        """Called internally by __call__ method to deseriaize JSONArray representation of objects.
        Raise :class:`~stargate.exception.DeserializationException` if operation fails.

        :param data: Array of JSON Objects.
        """
        result = []
        for instance in data:
            try:
                deserialized = self._deserialize_one(instance)
                result.append(deserialized)
            
            except DeserializationException as exception:
                raise DeserializationException(instance, str(exception))
        
        return result

    def _deserialize_one(self, instance):
        """Called internally by __call__ method to deseriaize JSONObject representation.
        Raise :class:`~stargate.exception.DeserializationException` if operation fails.
        Raise :class:`~stargate.exception.UnknownRelation` if unknown relation name is provided
        in `_embedded` key.Raise :class:`~stargate.exception.UnknownField` if unknown field is provided
        in relation `data` key or primary resource `data` key.

        :param instance: Array of JSON Objects.
        """
        try:
            for field in instance:
                
                if field == SerializationConst.EMBEDDED:
                    for relation in instance[SerializationConst.EMBEDDED]:
                        if not has_field(self.model, relation):
                            raise UnknownRelation(relation, self.model)
                
                elif field == SerializationConst.ATTRIBUTES:
                    for attribute in instance[SerializationConst.ATTRIBUTES]:
                        if not has_field(self.model, attribute):
                            raise UnknownField(attribute, self.model)
            links = {}
            links = instance.pop(SerializationConst.EMBEDDED, {})
            related_resources = {}

            for rel_name, rel_object in links.items():

                if SerializationConst.DATA in rel_object:
                    related_model = get_related_model(self.model, rel_name)
                    deserialize = RelDeserializer(self.session, related_model, rel_name)
                    related_resources[rel_name] = deserialize(rel_object[SerializationConst.DATA])
                else:
                    raise MissingData(rel_name)
            
            data = instance.pop(SerializationConst.ATTRIBUTES, {})
            data = dict((k, string_to_datetime(self.model, k, v)) for k, v in data.items())
            
            instance = self.model(**data)
            
            for relation_name, related_value in related_resources.items():
                setattr(instance, relation_name, related_value)
            return instance
        
        except DeserializationException as exception:
            raise DeserializationException(instance, str(exception))

class RelDeserializer(Deserializer):
    """Relation deserializer. Can deserialize TO_ONE or TO_MANY resources.
    
    :param session: SQLALchemy session object.
    :param model: Related Resource model class.

    """
    def __init__(self, session, model, relation_name = None):

        super(RelDeserializer, self).__init__(model, session)
    
    def __call__(self, data):

        #If its a TO_ONE relationship check: 
        #if primary key id is present return the object, if not present create and return new object
        if not isinstance(data, list):
            pk_name = resource_info(ResourceInfoConst.PRIMARY_KEY, self.model)
            
            if pk_name in data:
                return get_resource(self.session, self.model, data[pk_name])
            
            else:
                return self.model(**data)
        
        #If TO_MANY recurse of each object and check above conditions.
        else:
            return list(map(self, data))