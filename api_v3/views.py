from rest_framework import generics, response, viewsets


from .support import JSONApiEndpoint
from .models import Profile, Ticket, Notification
from .serializers import(
    ProfileSerializer,
    TicketSerializer,
    NotificationSerializer
)


class SessionEndpoint(generics.GenericAPIView):
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)


class TicketsEndpoint(JSONApiEndpoint, viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class UsersEndpoint(JSONApiEndpoint, viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class NotificationsEndpoint(JSONApiEndpoint, viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
