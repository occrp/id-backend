import json

from django.db import models
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

class DisplayMixin(object):
    """
    Renders a field's value in a display-friendly way. Should only be mixed
    in with models. It really should be accessible from properties but
    I didn't want to subclass all ndb field types.
    """
    def get_display_value(self, property_name):
        prop = getattr(self, property_name)
        value = (prop._get_display_value(self)
                 if hasattr(prop, '_get_display_value')
                 else getattr(self, property_name))

        if isinstance(value, list):
            value = ', '.join(value)

        return value

class JSONResponseMixin(object):
    def get(self, request):
        return self.render_to_response(request)

    def post(self, request):
        return self.render_to_response(request)

    def render_to_response(self, request):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json())

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return HttpResponse(content,
                            content_type='application/json',
                            **httpresponse_kwargs)

    def convert_context_to_json(self):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        def handledefault(o):
            if hasattr(o, "to_json"):
                return o.to_json()
            elif hasattr(o, "__dict__"):
                return o.__dict__
            else:
                raise ValueError("Not JSON serializable. Add to_json() or __dict__")
        return json.dumps(self.get_context_data(), default=handledefault)


class MessageMixin(object):
    def add_message(self, message, level='success'):
        # if isinstance(message, LazyProxy):
        #    message = unicode(message)
        print dir(self.request.session)
        if not hasattr(self, "messages"):
            self.messages = []
        self.messages.append((message, level))

class ModelDiffMixin(object):
    """
    Provide an API to determine what fields changed before a model is saved.
    """
    @property
    def diff(self):
        if self.is_new:
            return {'old': None, 'changed_properties': []}

        properties = [p for p in type(self)._properties if p != 'class']
        changed_properties = []
        old = self.key.get()
        new = self

        for prop in properties:
            d1_val = getattr(old, prop)
            d2_val = getattr(new, prop)
            if d1_val != d2_val:
                changed_properties.append(prop)
        return {'old': old, 'changed_properties': changed_properties}

    @property
    def is_new(self):
        return not bool(self.key)