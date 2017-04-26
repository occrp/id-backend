import rest_framework.generics
import rest_framework.viewsets

from .models import Profile, Ticket
from .serializers import ProfileSerializer, TicketSerializer
from .support import JSONApiEndpoint


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
