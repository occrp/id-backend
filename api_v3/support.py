import rest_framework.exceptions
import rest_framework.parsers
import rest_framework.renderers
import rest_framework.response
import rest_framework.authentication
import rest_framework_json_api.metadata
import rest_framework_json_api.parsers
import rest_framework_json_api.renderers
import rest_framework_json_api.utils
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY


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
    metadata_class = rest_framework_json_api.metadata.JSONAPIMetadata

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
