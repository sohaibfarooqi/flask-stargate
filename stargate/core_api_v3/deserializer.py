from .broker import url_for, serializer_for, primary_key_for, collection_name, model_for

"""Deserialization Exception Classes"""

class DeserializationException(Exception):
    
    def __init__(self, *args, **kw):
        super(DeserializationException, self).__init__(*args, **kw)

        self.detail = None

    def message(self):
        base = 'Failed to deserialize object'
        if self.detail is not None:
            return '{0}: {1}'.format(base, self.detail)
        return base

class ClientGeneratedIDNotAllowed(DeserializationException):
    def __init__(self, *args, **kw):
        super(ClientGeneratedIDNotAllowed, self).__init__(*args, **kw)

        self.detail = 'Server does not allow client-generated IDS'

class MissingInformation(DeserializationException):
    element = None

    def __init__(self, relation_name=None, *args, **kw):
        super(MissingInformation, self).__init__(*args, **kw)

        self.relation_name = relation_name

        if relation_name is None:
            detail = 'missing "{0}" element'
            detail = detail.format(self.element)
        else:
            detail = ('missing "{0}" element in linkage object for'
                      ' relationship "{1}"')
            detail = detail.format(self.element, relation_name)
        self.detail = detail


class MissingData(MissingInformation):
    element = 'data'


class MissingID(MissingInformation):
    element = 'id'


class MissingType(MissingInformation):
    element = 'type'

class ConflictingType(DeserializationException):
    def __init__(self, expected_type, given_type, relation_name=None, *args,
                 **kw):
        super(ConflictingType, self).__init__(*args, **kw)

        self.relation_name = relation_name

        self.expected_type = expected_type

        self.given_type = given_type

        if relation_name is None:
            detail = 'expected type "{0}" but got type "{1}"'
            detail = detail.format(expected_type, given_type)
        else:
            detail = ('expected type "{0}" but got type "{1}" in linkage'
                      ' object for relationship "{2}"')
            detail = detail.format(expected_type, given_type, relation_name)
        self.detail = detail
######################################################################################################

class Deserializer(object):
    def __init__(self, session, model):
        self.session = session
        self.model = model

    def __call__(self, document):
        raise NotImplementedError

class DefaultDeserializer(Deserializer):
    def __init__(self, session, model, allow_client_generated_ids=False, **kw):
        super(DefaultDeserializer, self).__init__(session, model, **kw)

        self.allow_client_generated_ids = allow_client_generated_ids

    def __call__(self, document):
        if 'data' not in document:
            raise MissingData
        data = document['data']
        if 'type' not in data:
            raise MissingType
        if 'id' in data and not self.allow_client_generated_ids:
            raise ClientGeneratedIDNotAllowed
        type_ = data.pop('type')
        expected_type = collection_name(self.model)
        if type_ != expected_type:
            raise ConflictingType(expected_type, type_)
        for field in data:
            if field == 'relationships':
                for relation in data['relationships']:
                    if not has_field(self.model, relation):
                        raise UnknownRelationship(relation)
            elif field == 'attributes':
                for attribute in data['attributes']:
                    if not has_field(self.model, attribute):
                        raise UnknownAttribute(attribute)
        links = {}
        if 'relationships' in data:
            links = data.pop('relationships', {})
            for link_name, link_object in links.items():
                if 'data' not in link_object:
                    raise MissingData(link_name)
                linkage = link_object['data']
                related_model = get_related_model(self.model, link_name)
                expected_type = collection_name(related_model)
                DRD = DefaultRelationshipDeserializer
                deserialize = DRD(self.session, related_model, link_name)
                links[link_name] = deserialize(linkage)
        pass
        data.update(data.pop('attributes', {}))
        data = strings_to_datetimes(self.model, data)
        instance = self.model(**data)
        for relation_name, related_value in links.items():
            setattr(instance, relation_name, related_value)
        return instance
