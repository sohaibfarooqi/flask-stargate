from .proxy import manager_info

"""Deserialization Exception Classes"""


class Deserializer(object):
    def __init__(self, session, model):
        self.session = session
        self.model = model

    def __call__(self, document):
        if 'data' not in document:
            raise MissingData
        data = document['data']
        if 'type' not in data:
            raise MissingType
        if 'id' in data and not self.allow_client_generated_ids:
            raise ClientGeneratedIDNotAllowed
        type_ = data.pop('type')
        expected_type = collection_name_for(self.model)
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
                expected_type = collection_name_for(related_model)
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
