import rest_framework.exceptions
import rest_framework.parsers
import rest_framework.renderers
import rest_framework.response
import rest_framework.authentication
import rest_framework.filters
import rest_framework_json_api.metadata
import rest_framework_json_api.parsers
import rest_framework_json_api.renderers
import rest_framework_json_api.pagination
import rest_framework_json_api.utils
import rest_framework_json_api.exceptions
import django_filters.rest_framework
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY
from querystring_parser import parser as qs_parser
from django.utils.six.moves.urllib.parse import unquote as url_unquote
from django.utils.encoding import force_unicode

from django.conf import settings


class DjangoFilterBackend(django_filters.rest_framework.DjangoFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)

        if not filter_class:
            return queryset

        params = view.extract_filter_params(request)

        return filter_class(params, queryset=queryset, request=request).qs


class OrderingFilter(rest_framework.filters.OrderingFilter):
    ordering_param = 'sort'
    ordering_fields = ('created_at', )


class Pagination(rest_framework_json_api.pagination.PageNumberPagination):
    page_query_param = 'page[number]'
    page_size_query_param = 'page[size]'
    page_size = 30

    def build_link(self, index):
        link = super(Pagination, self).build_link(index)
        if link:
            link = url_unquote(link)
        return force_unicode(link)

    def get_paginated_response(self, data):
        """Remove pagination from meta. Not needed, handled by links."""
        response = super(Pagination, self).get_paginated_response(data)
        response.data['meta'].pop('pagination', None)
        return response


class SessionAuthenticationSansCSRF(
        rest_framework.authentication.SessionAuthentication):

    def enforce_csrf(self, request):
        return


class JSONApiEndpoint(object):
    """Generic mixin for our endpoints to enable JSON API format.

    See: https://github.com/django-json-api/django-rest-framework-json-api/blob/develop/example/views.py  # noqa
    """
    parser_classes = [
        rest_framework_json_api.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser,
    ]
    renderer_classes = set([
        rest_framework_json_api.renderers.JSONRenderer,
        rest_framework.renderers.BrowsableAPIRenderer
    ])

    if (not settings.DEBUG):
        renderer_classes.remove(rest_framework.renderers.BrowsableAPIRenderer)

    authentication_classes = [
        SessionAuthenticationSansCSRF,
    ]
    filter_backends = [
        OrderingFilter,
        DjangoFilterBackend
    ]
    pagination_class = Pagination
    metadata_class = rest_framework_json_api.metadata.JSONAPIMetadata
    filter_fields = ('id', )

    def extract_filter_params(self, request):
        params = qs_parser.parse(request.META['QUERY_STRING'])
        params = params.get('filter') or {}

        for k, v in params.items():
            if not v:
                params.pop(k)

        return params

    def action_name(self):
        """Simple helper to generate the current action name."""
        template = '{}:{}'
        resource = self.queryset.model.__name__.lower()
        return template.format(resource, self.action).replace('partial_', '')

    def handle_exception(self, exc):
        context = self.get_exception_handler_context()
        response = rest_framework_json_api.exceptions.exception_handler(
            exc, context)

        if response is None:
            self.raise_uncaught_exception(exc)

        if isinstance(exc, rest_framework.exceptions.ValidationError):
            # For ember-data validation errors (isInvalid method on adapter)
            response.status_code = HTTP_422_UNPROCESSABLE_ENTITY

        return response
