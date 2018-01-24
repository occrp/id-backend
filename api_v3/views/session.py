from rest_framework import response, viewsets

from api_v3.serializers import ProfileSerializer


class SessionEndpoint(viewsets.GenericViewSet):
    serializer_class = ProfileSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)
