from flask.views import MethodView

class Api:
    def __init__(self, blueprint):
        self.blueprint = blueprint

    def route(self, url, pk_name='pk', pk_type='int'):
        def decorator(resource):
            view_func = resource.as_view(resource.__name__)
            self.blueprint.add_url_rule(url,
                                        defaults={pk_name: None},
                                        view_func=view_func,
                                        methods=['GET'])
            self.blueprint.add_url_rule(url, view_func=view_func,
                                        methods=['POST'])
            self.blueprint.add_url_rule('{}/<{}:{}>'.format(url, pk_type, pk_name),
                                        view_func=view_func,
                                        methods=['GET', 'PUT', 'DELETE'])
            return resource
        return decorator

    def custom_route(self, url):
        def decorator(resource):
            self.blueprint.add_url_rule(url, view_func=resource,
                                        methods=['POST'])
            return resource
        return decorator


class Resource(MethodView):
    pass
