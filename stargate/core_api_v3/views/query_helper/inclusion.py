def get_all_inclusions(self, instance_or_instances):
        if isinstance(instance_or_instances, Query):
            to_include = set(chain(self.resources_to_include(resource)
                                   for resource in instance_or_instances))
        else:
            to_include = self.resources_to_include(instance_or_instances)
        return self._serialize_many(to_include)
    
    
    def resources_to_include(self, instance):
        toinclude = request.args.get('include')
        if toinclude is None and self.default_includes is None:
            return {}
        elif toinclude is None and self.default_includes is not None:
            toinclude = self.default_includes
        else:
            toinclude = set(toinclude.split(','))
        return set(chain(resources_from_path(instance, path)
                         for path in toinclude))