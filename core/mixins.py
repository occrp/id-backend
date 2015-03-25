import json

from django.core.urlresolvers import reverse, reverse_lazy
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

class PrettyPaginatorMixin(object):

    def create_page_object(self, page_num, is_current_page, url_name, url_args):
        obj = {'page_num': page_num,
               'is_current_page': is_current_page,
               'url': reverse_lazy(url_name, kwargs={'page': page_num})}

        return obj

    def create_pretty_pagination_object(self,
                                        paginator,
                                        page_number,
                                        max_page_buttons,
                                        page_padding,
                                        url_name,
                                        url_args,
                                        ellipsis=True):
        obj = {}
        obj['paginator'] = paginator
        obj['page_objects'] = []

        total_pages = paginator.num_pages
        current_page = page_number

        if paginator.count <= max_page_buttons:
            for i in range(1, paginator.count + 1):
                is_current = True if i == current_page else False
                obj['page_objects'].append(self.create_page_object(i, is_current, url_name, url_args))

        else:
            padded_page_start = current_page - page_padding

            if padded_page_start <= 1:
                padded_page_start = 2

            padded_page_end = (page_padding * 2) + padded_page_start + 1

            if padded_page_end > total_pages:
                padded_page_end = total_pages
                padded_page_start = total_pages - (page_padding * 2 + 1)

            obj['page_objects'] = [self.create_page_object(1,
                                                           self.is_current_page(1, page_number),
                                                           url_name,
                                                           url_args)]

            for i in range(padded_page_start, padded_page_end):

                obj['page_objects'].append(self.create_page_object(i,
                                           self.is_current_page(i, current_page),
                                           url_name,
                                           url_args))

            obj['page_objects'].append(self.create_page_object(total_pages,
                                                               self.is_current_page(total_pages, current_page),
                                                               url_name,
                                                               url_args))

            if ellipsis:
                if current_page - page_padding > 1:
                    obj['page_objects'].insert(1, {'spacer': True})
                if current_page + page_padding < total_pages - 1:
                    obj['page_objects'].insert(len(obj['page_objects'])-1, {'spacer': True})

        print padded_page_start
        print obj
        return obj

    def is_current_page(self, page_num, current_page_num):
        return True if page_num == current_page_num else False
