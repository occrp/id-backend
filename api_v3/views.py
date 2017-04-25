from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import ProfileSerializer


class SessionEndpoint(GenericAPIView):
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        # based on RetrieveModelMixin
        # (it doesn't pass request to get_object, so we can't use that)
        instance = self.get_object(request)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self, request, *args, **kwargs):
        return request.user
