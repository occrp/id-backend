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
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY
from querystring_parser import parser as qs_parser


class DjangoFilterBackend(rest_framework.filters.DjangoFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)
        params = qs_parser.parse(request.META['QUERY_STRING'])
        params = params.get('filter') or {}

        if filter_class:
            return filter_class(params, queryset=queryset, request=request).qs

        return queryset


class OrderingFilter(rest_framework.filters.OrderingFilter):
    ordering_param = 'sort'
    ordering_fields = ('created_at', )


class Pagination(rest_framework_json_api.pagination.PageNumberPagination):
    page_query_param = 'page[number]'
    paginate_by_param = 'page[size]'


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
    renderer_classes = [
        rest_framework_json_api.renderers.JSONRenderer,
        rest_framework.renderers.BrowsableAPIRenderer,
    ]
    authentication_classes = [
        rest_framework.authentication.BasicAuthentication,
        SessionAuthenticationSansCSRF
    ]
    filter_backends = [
        OrderingFilter,
        DjangoFilterBackend
    ]
    pagination_class = Pagination
    metadata_class = rest_framework_json_api.metadata.JSONAPIMetadata
    filter_fields = ('created_at', )

    def handle_exception(self, exc):
        if isinstance(exc, rest_framework.exceptions.ValidationError):
            # some require that validation errors return 422 status
            # for example ember-data (isInvalid method on adapter)
            exc.status_code = HTTP_422_UNPROCESSABLE_ENTITY
        # exception handler can't be set on class so you have to
        # override the error response in this method
        response = super(JSONApiEndpoint, self).handle_exception(exc)
        context = self.get_exception_handler_context()
        return rest_framework_json_api.utils.format_drf_errors(
            response, context, exc)
