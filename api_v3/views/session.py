from rest_framework import response, viewsets

from api_v3.models import Profile
from api_v3.serializers import ProfileSerializer
from .support import JSONApiEndpoint


class SessionEndpoint(JSONApiEndpoint, viewsets.GenericViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.none()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)

    def get_serializer_context(self):
        context = super(SessionEndpoint, self).get_serializer_context()
        context['add_misc'] = True
        return context
