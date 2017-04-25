import rest_framework.exceptions
import rest_framework.generics
import rest_framework.parsers
import rest_framework.renderers
import rest_framework.response
import rest_framework.viewsets
import rest_framework_json_api.metadata
import rest_framework_json_api.parsers
import rest_framework_json_api.renderers
import rest_framework_json_api.utils

from .models import Profile, Ticket
from .serializers import ProfileSerializer, TicketSerializer


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
    metadata_class = rest_framework_json_api.metadata.JSONAPIMetadata

    def handle_exception(self, exc):
        if isinstance(exc, rest_framework.exceptions.ValidationError):
            # some require that validation errors return 422 status
            # for example ember-data (isInvalid method on adapter)
            exc.status_code = 422
        # exception handler can't be set on class so you have to
        # override the error response in this method
        response = super(JSONApiEndpoint, self).handle_exception(exc)
        context = self.get_exception_handler_context()
        return rest_framework_json_api.utils.format_drf_errors(
            response, context, exc)


class SessionEndpoint(rest_framework.generics.GenericAPIView):
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return rest_framework.response.Response(serializer.data)


class TicketsEndpoint(JSONApiEndpoint, rest_framework.viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class UsersEndpoint(JSONApiEndpoint, rest_framework.viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
