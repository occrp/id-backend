import json
import csv
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import models
from django.db.models import Q
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify

from core.utils import json_dumps
from core.models import Notification, NotificationSubscription, notification_channel_format

from id.constdata import *

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
        return json_dumps(self.get_context_data())


class CSVResponder(object):
    def render_csv(self, context):
        if hasattr(self, "CONTEXT_TITLE_KEY"):
            title = unicode(context[self.CONTEXT_TITLE_KEY])
        else:
            title = unicode(context['title'])

        if hasattr(self, "CONTEXT_ITEMS_KEY"):
            ctxkey = self.CONTEXT_ITEMS_KEY
        else:
            ctxkey = 'items'

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment; filename="%s.csv"'
                                           % slugify(title))

        writer = csv.writer(response)

        for item in context[ctxkey]:
            writer.writerow(item.as_sequence())

        return response

class JSONResponder(object):
    def render_json(self, context):
        if hasattr(self, "CONTEXT_TITLE_KEY"):
            title = unicode(context[self.CONTEXT_TITLE_KEY])
        else:
            title = unicode(context['title'])

        response = HttpResponse(content_type='text/json')
        response['Content-Disposition'] = ('attachment; filename="%s.json"'
                                           % slugify(title))
        response.write(json_dumps(self.get_context_data()))

        return response

class CSVorJSONResponseMixin(CSVResponder, JSONResponder):
    def render_to_response(self, context, **response_kwargs):
        if 'csv' in self.request.GET.get('format', ''):
            return self.render_csv(context)
        elif 'json' in self.request.GET.get('format', ''):
            return self.render_json(context)
        elif self.request.is_ajax():
            return self.render_json(context)
        else:
            return super(CSVorJSONResponseMixin, self).render_to_response(context, **response_kwargs)

class MessageMixin(object):
    def add_message(self, message, level='success'):
        # if isinstance(message, LazyProxy):
        #    message = unicode(message)
        print dir(self.request.session)
        if not hasattr(self, "messages"):
            self.messages = []
        self.messages.append((message, level))

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
                if padded_page_start <= 1: padded_page_start = 2

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

        return obj

    def is_current_page(self, page_num, current_page_num):
        return True if page_num == current_page_num else False


class NotificationMixin(object):
    def channel_components(self, channel):
        components = ("project", "module", "model", "instance", "action")
        return dict(zip(components, channel.split(":")))

    def get_notification_channel_subscribers(self, channel):
        assert(notification_channel_format.match(channel))
        components = self.channel_components(channel)

        terms = ((Q(project=components["project"]) | Q(project=None))
               & (Q(module=components["module"]) | Q(module=None))
               & (Q(model=components["model"]) | Q(model=None))
               & (Q(instance=components["instance"]) | Q(instance=None))
               & (Q(action=components["action"]) | Q(action=None))
               )

        return set([ns.user for ns in NotificationSubscription.objects.filter(terms)])

    def get_channel(self, action="none"):
        dets = {
            "project":  "id",
            "module": self.__module__.split(".")[0].lower(),
            "model": self.__class__.__name__.lower(),
            "instance": self.id,
            "action": action.lower()
        }
        return "%(project)s:%(module)s:%(model)s:%(instance)s:%(action)s" % dets

    def notify(self, text, urlname=None, params={}, action="none"):
        channel = self.get_channel(action)
        subs = self.get_notification_channel_subscribers(channel)
        for user in subs:
            m = Notification()
            m.create(user, channel, text, urlname, params)
